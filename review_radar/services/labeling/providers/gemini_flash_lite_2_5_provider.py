from typing import Dict, Any, List, Optional
import json
import logging

import google.generativeai as genai
from dotenv import load_dotenv
import os

from .base_provider import BaseLabelingProvider, LabelResult


class GeminiFlashLite25Provider(BaseLabelingProvider):
    """
    Gemini Flash Lite 2.5 provider for labeling
    
    Model ID is a class constant and cannot be changed.
    """
    
    # Class constant - cannot be changed per instance
    MODEL_ID: str = "models/gemini-2.5-flash-lite"
    
    def __init__(self, aspects: list[str], logger: Optional[logging.Logger] = None):
        super().__init__(logger=logger)
        
        self.aspects = aspects
        
        # Initialize Gemini API key
        load_dotenv()  # Load environment variables from .env file
        genai.configure(api_key=os.environ.get("GEMINI_KEY"))

        try:
            self.model_info = [m for m in genai.list_models() if m.name == self.MODEL_ID][0]
        except IndexError:
            self._log(f"Model {self.MODEL_ID} not found in Gemini model info.", level="error")
            raise ValueError(f"Model {self.MODEL_ID} not found in Gemini model info.")
        
        self.generation_config = {
            "temperature": 0.1,  # ตั้งค่าต่ำเพื่อให้ผลลัพธ์คงที่ (Deterministic) ไม่เปลี่ยนไปมา
            "top_p": 0.95,
            "max_output_tokens": 100, # บังคับให้หยุดพ่นถ้าเกิน 100 tokens (ประหยัดเงิน)
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "array",
                "items": {
                    "type": "array",
                    "items": {
                        "type": "number",
                        "nullable": True  # อนุญาตให้มี null ได้ (สำหรับฝั่ง Score)
                    },
                },
            }
        }

        self.system_instructions = self._make_system_instructions()

        self.model = genai.GenerativeModel(
            self.MODEL_ID, 
            generation_config=self.generation_config, 
            system_instruction=self.system_instructions)

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return self.model_info
    
    def ark_llm(self, text: str) -> List[float | None]:
        """Call Gemini API to label review"""
        response = self.model.generate_content(text)

        return response  # type: ignore
    
    def _make_system_instructions(self) -> str:
        """Create system instructions for Gemini prompt"""
        return f"""Role: High-Precision Thai Restaurant ABSA Annotator
Task: Extract Score (S) and Confidence (C) for 5 aspects.

Aspects: {', '.join(self.aspects)}

Rules for Confidence (C):
- Score (S) range: -1.0 (Very Negative) to 1.0 (Very Positive). If not mentioned, use null.
- If S is provided: C = Confidence that the score is accurate.
- If S is null: C = Confidence that this aspect is NOT mentioned in the text at all.
- C range: 0.0 to 1.0 (1.0 = Absolutely certain), Important: Not null.

Conflict Handling: If a review has mixed feedback (e.g., "Good food but oily"), provide a balanced Score (S) and lower the Confidence (C) to reflect the ambiguity.

Output Format: Strict JSON [[S1,S2,S3,S4,S5], [C1,C2,C3,C4,C5]]"""

    def parser_label(self, response:str) -> tuple[List[float | None], List[float]]:
        """Validate LLM response format"""
        try:
            parsed = json.loads(response)
        except json.JSONDecodeError:
            self._log(f"JSON decode error for response: {response}", level="error")
            raise ValueError(f"Response is not valid JSON: {response}")
        if not (isinstance(parsed, list) and len(parsed) == 2):
            raise ValueError(f"Response must be a list of two lists, {response}")
        scores, confidences = parsed
        if not (isinstance(scores, list) and isinstance(confidences, list)):
            raise ValueError(f"Both elements must be lists, {response}")
        if not (len(scores) == len(self.aspects) and len(confidences) == len(self.aspects)):
            raise ValueError(f"Both lists must match number of aspects, {response}")
        for s in scores:
            if s is not None and not (-1.0 <= s <= 1.0):
                raise ValueError(f"Scores must be between -1.0 and 1.0 or null, {response}")
        for c in confidences:
            if not (0.0 <= c <= 1.0):
                raise ValueError(f"Confidences must be between 0.0 and 1.0, {response}")
        return scores, confidences

    def process_label(
        self,
        review_text: str
    ) -> LabelResult:
        """Process labeling for a single review text"""
        response = self.ark_llm(review_text)
        """response looks like this:
        GenerateContentResponse(
            done=True,
            iterator=None,
            result=protos.GenerateContentResponse({
            "candidates": [
                {
                "content": {
                    "parts": [
                    {
                        "text": "[[0.6, 0.8, -0.8, null, null], [0.8, 0.7, 0.9, 1.0, 1.0]]"
                    }
                    ],
                    "role": "model"
                },
                "finish_reason": "STOP",
                "index": 0
                }
            ],
            "usage_metadata": {
                "prompt_token_count": 441,
                "candidates_token_count": 44,
                "total_token_count": 485
            },
            "model_version": "gemini-2.5-flash-lite"
            }),
        )
        """
        
        # Parse output
        try:
            scores, confidences = self.parser_label(response.text)
        except (ValueError, TypeError) as e:
            self._log(f"Label parsing error: {e}\nreview: {review_text}\naspects: {self.aspects} response: {response.text}", level="error")
            raise e

        labels = {}
        for i, aspect in enumerate(self.aspects):
            labels[aspect] = {
                'score': scores[i],
                'confidence': confidences[i]
            }

        metadata = {}
        response_dict = response.to_dict()
        metadata['usage_metadata'] = response_dict['usage_metadata']
        metadata['text_len'] = len(review_text)
        metadata['model_version'] = response_dict['model_version']
        metadata

        return LabelResult(
            labels=labels,
            metadata=metadata
        )
