import json

import re


import urllib.request








class StructuredLLMService:


    def __init__(


        self,


        model="qwen2.5:7b",


        base_url="http://127.0.0.1:11434",


    ):


        self.model = model


        self.base_url = base_url.rstrip("/")





    def generate(self, question: str, chunks: list[dict]) -> dict:


        if not isinstance(question, str) or not question.strip():


            raise ValueError("question must not be empty")





        if not chunks:


            raise ValueError("chunks must not be empty")







        response_language = (

            "Arabic"

            if re.search(r"[\u0600-\u06FF]", question)

            else "English"

        )



        sources = [


            {


                "id": f"S{i}",


                "page": chunk["page_number"],


                "text": chunk["chunk_text"],


            }


            for i, chunk in enumerate(chunks, 1)


        ]





        source_map = {


            source["id"]: source["page"]


            for source in sources


        }





        schema = {


            "type": "object",


            "properties": {


                "items": {


                    "type": "array",


                    "items": {


                        "type": "object",


                        "properties": {


                            "fact": {"type": "string"},


                            "source_id": {


                                "type": "string",


                                "enum": list(source_map),


                            },


                        },


                        "required": ["fact", "source_id"],


                        "additionalProperties": False,


                    },


                },


            },


            "required": ["items"],


            "additionalProperties": False,


        }





        payload = {


            "model": self.model,


            "messages": [


                {


                    "role": "system",


                    "content": (


                        "You answer questions about PDF documents. "


                        "Answer in the same language as the question. "

                        "Follow response_language exactly. "

                        "For English, use fluent English sentences only. "

                        "For Arabic, use fluent Arabic sentences only, "

                        "except technical names. "

                        "Do not repeat the same fact in different items. "

                        "For Arabic questions, write facts in clear Arabic. "

                        "Preserve technical names in English. "

                        "Answer only the specific question asked. "

                        "Exclude unrelated facts and requirements. "

                        "For yes/no questions, give a direct yes or no. "
                        "For yes/no questions containing negation, distinguish "
                        "between evidence supporting and contradicting the claim. "
                        "If sources contradict the negative claim, answer No "
                        "and cite the supporting evidence. "
                        "Do not return an empty array merely because the "
                        "negative claim is false. "
                        "Return an empty array if evidence is insufficient. "


                        "Use only facts explicitly supported by sources. "
                        "Preserve exact numeric values from sources, "
                        "including decimal places, percentages, and units. "
                        "Never round or approximate numbers. "
                        "Never confuse accuracy, precision, recall, "
                        "F1-score, or other distinct metrics. "


                        "Return concise factual items. "


                        "Each item must identify its supporting source. "


                        "Use natural Arabic grammar when responding in Arabic. "
                        "Translate ordinary English verbs into Arabic. "
                        "Keep established technical names in English, such as SVM and Decision Tree. "
                        "Do not invent or alter source facts when improving language. "
                        "Preserve technical terms in English. "


                        "Never copy truncated words. "


                        "Never invent facts, requirements, or source IDs. "


                        "Distinguish mandatory requirements from examples. "


                        "If sources are insufficient, return an empty items array."


                    ),


                },


                {


                    "role": "user",


                    "content": (


                        "Question: What does the application do?\\n"


                        "Source S1: The application reads CSV files "


                        "and generates reports."


                    ),


                },


                {


                    "role": "assistant",


                    "content": json.dumps(


                        {


                            "items": [


                                {


                                    "fact": "The application reads CSV files.",


                                    "source_id": "S1",


                                },


                                {


                                    "fact": "The application generates reports.",


                                    "source_id": "S1",


                                },


                            ]


                        }


                    ),


                },


                *([
                {

                    "role": "user",

                    "content": json.dumps(

                        {

                            "question": "\u0647\u0644 \u064a\u062c\u0628 \u0627\u0633\u062a\u062e\u062f\u0627\u0645 Django \u0648Flask \u0645\u0639\u0627\u061f",

                            "sources": [

                                {

                                    "id": "S1",

                                    "page": 1,

                                    "text": "Use either Django or Flask.",

                                }

                            ],

                        },

                        ensure_ascii=False,

                    ),

                },

                {

                    "role": "assistant",

                    "content": json.dumps(

                        {

                            "items": [

                                {

                                    "fact": "\u0644\u0627\u060c \u0627\u0644\u0645\u0637\u0644\u0648\u0628 \u0627\u0633\u062a\u062e\u062f\u0627\u0645 Django \u0623\u0648 Flask\u060c \u0648\u0644\u064a\u0633 \u0643\u0644\u064a\u0647\u0645\u0627 \u0645\u0639\u0627.",

                                    "source_id": "S1",

                                }

                            ]

                        },

                        ensure_ascii=False,

                    ),

                },
                ] if response_language == "Arabic" else []),

                {


                    "role": "user",


                    "content": json.dumps(


                        {


                            "question": question,

                            "response_language": response_language,


                            "sources": sources,


                        },


                        ensure_ascii=False,


                    ),


                },


            ],


            "format": schema,


            "stream": False,


            "options": {


                "temperature": 0,


                "num_ctx": 8192,


                "num_predict": 650,


            },


        }





        request = urllib.request.Request(


            f"{self.base_url}/api/chat",


            data=json.dumps(payload).encode("utf-8"),


            headers={"Content-Type": "application/json"},


            method="POST",


        )





        with urllib.request.urlopen(


            request,


            timeout=300,


        ) as response:


            data = json.loads(response.read().decode("utf-8"))





        if data.get("done_reason") != "stop":


            raise RuntimeError("LLM did not finish generating")





        content = (data.get("message") or {}).get("content", "")


        result = json.loads(content)





        if not isinstance(result, dict) or set(result) != {"items"}:


            raise ValueError("Invalid structured response")





        items = result["items"]





        if not isinstance(items, list):


            raise ValueError("Invalid items array")





        validated_items = []

        seen_facts = set()





        for item in items:


            if (


                not isinstance(item, dict)


                or set(item) != {"fact", "source_id"}


                or not isinstance(item["fact"], str)


                or not item["fact"].strip()


                or not isinstance(item["source_id"], str)


                or item["source_id"] not in source_map


            ):


                raise ValueError("Invalid fact or source citation")







            normalized_fact = " ".join(

                item["fact"].split()

            ).casefold()



            if normalized_fact in seen_facts:

                continue



            seen_facts.add(normalized_fact)



            validated_items.append(


                {


                    "fact": item["fact"].strip(),


                    "source_id": item["source_id"],


                    "page_number": source_map[item["source_id"]],


                }


            )





        return {


            "items": validated_items,


            "source_count": len(sources),


            "model": self.model,


        }


