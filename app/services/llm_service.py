from typing import Dict, Optional
from openai import OpenAI
from app.core.config import settings
from app.core.prompt_templates import ProductPrompts
import logging
import json

logger = logging.getLogger(__name__)

class LLMService:
    """Service for handling LLM-related operations."""
    
    def __init__(self):
        self.recommend_client = OpenAI(api_key=settings.DOUBAO_API_KEY, base_url=settings.DOUBAO_BASE_URL)
        self.recommend_model = settings.DOUBAO_MODEL
        self.client = OpenAI(api_key=settings.VLLM_API_KEY, base_url=settings.VLLM_BASE_URL)
        self.model = settings.VLLM_MODEL

    async def get_product_recommendations(self, user_query: str):
        try:
            response = self.recommend_client.chat.completions.create(
                model=self.recommend_model,
                messages=[
                    {"role": "system", "content": ProductPrompts.SEARCH_SYSTEM_MESSAGE},
                    {"role": "user", "content": user_query}
                ],
                timeout=settings.OPENAI_TIMEOUT
            )
            
            if not response or not response.choices or not response.choices[0].message:
                logger.error("Invalid response format from LLM")
                return None
                
            content = response.choices[0].message.content
            if not content or not isinstance(content, str):
                logger.error(f"Invalid content format: {content}")
                return None
                
            return content
            
        except Exception as e:
            logger.error(f"Error in get_product_recommendations: {str(e)}")
            return None

    async def select_best_products_from_web(
        self,
        user_query: str,
        web_search_result: str,
        num_products: int = 3,
        stream: bool = False
    ) :
        try:
            user_message = ProductPrompts.SELECT_PRODUCTS_FROM_WEB.format(
                user_query=user_query,
                web_search_result=web_search_result,
                num_products=num_products,
            )
            logger.info(user_message)
            
            if not stream:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": ProductPrompts.PRODUCT_RECOMMENDATION},
                        {"role": "user", "content": user_message}
                    ]
                )
                if not response or not response.choices or not response.choices[0].message:
                    logger.error("Invalid response format from LLM")
                    return None

                content = response.choices[0].message.content
                if not content or not isinstance(content, str):
                    logger.error(f"Invalid content format: {content}")
                    return None
                return content
            
            else:
                stream_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": ProductPrompts.PRODUCT_RECOMMENDATION},
                        {"role": "user", "content": user_message}
                    ],
                    stream=True
                )
                return stream_response
        except Exception as e:
            print(e)
            logger.error(f"Error in select_best_products_from_web: {str(e)}")
            return None

    async def select_best_products(
        self,
        user_query: str,
        llm_response: str,
        search_results: dict,
        num_products: int = 3
    ) -> Dict:
        """Select the best products based on user query and search results.
        
        Args:
            user_query: Original user query
            llm_response: Previous LLM recommendation response
            search_results: Product search results
            language: Response language (default: Chinese)
            num_products: Number of products to recommend
            
        Returns:
            Dict containing full response and structured data
        """
        try:
            user_message = ProductPrompts.SELECT_PRODUCT_PRODUCTS.format(
                user_query=user_query,
                ai_select=llm_response,
                web_search_result=search_results,
                num_products=num_products,
                json=__import__('json'),
                products=products if products else []
            )
            
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": settings.SELECT_BEST_PRODUCTS_SYSTEM_MESSAGE},
                    {"role": "user", "content": user_message}
                ],
                stream=True
            )
            
            full_response = ""
            json_part = ""
            json_started = False
            
            # Process streaming response
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)  # Stream output to console
                    full_response += content
                    
                    # Check for JSON markers
                    if "---JSON数据开始---" in content and not json_started:
                        json_started = True
                    elif json_started:
                        json_part += content
                        if "---JSON数据结束---" in content:
                            # End of JSON part detected
                            json_part = json_part.replace("---JSON数据结束---", "").strip()
                            break
            
            print()  # Add newline after streaming
            
            # Extract and parse JSON data
            if json_part:
                try:
                    # Clean up JSON string for parsing
                    json_part = json_part.strip()
                    # Handle possible trailing commas in arrays
                    json_part = json_part.replace(",\n  ]", "\n  ]").replace(",\n]", "\n]")
                    
                    # Parse JSON
                    json_data = json.loads(json_part)
                    
                    # Return both full text and structured data
                    return {
                        "full_response": full_response,
                        "structured_data": json_data
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析错误: {e}")
                    logger.error(f"错误的JSON字符串: {json_part}")
                    # Return just the full text if JSON parsing fails
                    return {
                        "full_response": full_response,
                        "structured_data": None
                    }
            
            return {
                "full_response": full_response,
                "structured_data": None
            }
                  
        except Exception as e:
            logger.error(f"精选商品时出错: {e}")
            return {
                "full_response": None,
                "structured_data": None
            }
    
    async def generate_product_recommendations(
        self,
        user_query: str,
        search_results: Optional[Dict] = None,
        num_recommendations: int = 3
    ) -> Dict:
        """Generate product recommendations based on user query.
        
        Args:
            user_query: User's product query
            search_results: Optional search results to base recommendations on
            num_recommendations: Number of products to recommend
            
        Returns:
            Dict containing recommendations and structured data
        """
        try:
            # Construct the prompt
            search_results_text = f"\n可用的产品数据：{search_results}" if search_results else ""
            user_message = ProductPrompts.RECOMMEND_PRODUCTS.format(
                num_recommendations=num_recommendations,
                user_query=user_query,
                search_results_text=search_results_text
            )
            
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                stream=True
            )
            
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            
            print()  # Add newline after streaming
            
            return {
                "full_response": full_response,
                "structured_data": None  # Implement structured data parsing if needed
            }
            
        except Exception as e:
            logger.error(f"生成商品推荐时出错: {e}")
            return {
                "full_response": None,
                "structured_data": None
            }