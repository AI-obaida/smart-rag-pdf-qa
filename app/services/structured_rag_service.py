from app.services.search_query_translator import SearchQueryTranslator
import re



from app.services.rag_service import RAGService

from app.services.chunk_expansion import ChunkExpansionService

from app.services.structured_llm_service import StructuredLLMService

from app.services.technical_entity_guard import TechnicalEntityGuard





class StructuredRAGService:

    def __init__(

        self,

        embedding_model,

        llm_service=None,

        citation_validator=None,

        relevance_guard=None,

        modality_guard=None,

    ):

        self.rag = RAGService(embedding_model)

        self.expansion = ChunkExpansionService()

        self.llm = (

            llm_service

            if llm_service is not None

            else StructuredLLMService()

        )

        self.citation_validator = citation_validator

        self.relevance_guard = relevance_guard

        self.modality_guard = modality_guard





    def _technical_entities_supported(self, fact, source_text):
        guard = TechnicalEntityGuard()

        if not isinstance(fact, str) or not isinstance(source_text, str):
            return False

        negative = re.search(
            r"\b(?:not|isn't|aren't|no|without)\b",
            fact,
            flags=re.IGNORECASE,
        )

        candidates = re.findall(
            r"(?<!\w)[A-Za-z][A-Za-z0-9+#-]*(?:\.[A-Za-z0-9+#-]+)*",
            fact,
        )

        common_words = {
            "the", "this", "that", "these", "those",
            "there", "here", "a", "an",
        }

        known_technologies = {
            "flask", "django", "fastapi",
            "postgresql", "sqlite", "mysql",
            "mongodb", "redis", "react",
            "angular", "docker", "pytorch",
            "tensorflow", "numpy", "pandas",
        }

        entities = {
            word
            for word in candidates
            if word.lower() not in common_words
            and (
                (len(word) >= 3)
                or any(char in "+#" for char in word)
            )
            and (
                word.lower() in known_technologies
                or any(char.isupper() for char in word[1:])
                or (
                    word[0].isupper()
                    and any(char in "+#" for char in word)
                )
                or (
                    word[0].isupper()
                    and word[1:].islower()
                    and fact.lstrip().startswith(word)
                )
            )
        }

        for entity in entities:
            escaped = re.escape(entity)

            negated_requirement = re.search(
                rf"(?<!\w){escaped}(?!\w)\s+is\s+not\s+required\b",
                fact,
                flags=re.IGNORECASE,
            )

            positive_requirement = re.search(
                rf"(?<!\w){escaped}(?!\w)\s+is\s+required\b",
                source_text,
                flags=re.IGNORECASE,
            )

            if negated_requirement and positive_requirement:
                return False

            if guard.contains_entity(source_text, entity):
                continue

            exclusive_requirement = (
                negative
                and re.search(
                    r"\bonly\s+.+?\s+is\s+required\b",
                    source_text,
                    flags=re.IGNORECASE,
                )
                and re.search(
                    r"\bis\s+not\s+required\b",
                    fact,
                    flags=re.IGNORECASE,
                )
            )

            if exclusive_requirement:
                continue

            return False

        return True

    def _validate_citations(self, items, chunks):

        sources = {

            "S" + str(index): chunk

            for index, chunk in enumerate(chunks, start=1)

        }



        accepted = []

        rejected = []



        for item in items:

            source_id = item.get("source_id")

            source = sources.get(source_id)



            if not source:

                rejected.append(item)

                continue



            verdict = self.citation_validator.evaluate(

                fact=item["fact"],

                source_text=source["chunk_text"],

            )



            supporting_source_id = None

            supporting_source = None



            if (

                verdict["verdict"] == "SUPPORTED"

                and self._technical_entities_supported(

                    item["fact"], source["chunk_text"]

                )

            ):

                supporting_source_id = source_id

                supporting_source = source



            elif verdict["verdict"] == "INSUFFICIENT":

                for candidate_id, candidate in sources.items():

                    if candidate_id == source_id:

                        continue



                    if candidate["page_number"] != source["page_number"]:

                        continue



                    candidate_verdict = self.citation_validator.evaluate(

                        fact=item["fact"],

                        source_text=candidate["chunk_text"],

                    )



                    if (

                        candidate_verdict["verdict"] == "SUPPORTED"

                        and self._technical_entities_supported(

                            item["fact"], candidate["chunk_text"]

                        )

                    ):

                        supporting_source_id = candidate_id

                        supporting_source = candidate

                        break



            if supporting_source is not None:

                corrected_item = dict(item)

                corrected_item["source_id"] = supporting_source_id

                corrected_item["page_number"] = supporting_source["page_number"]

                accepted.append(corrected_item)

            else:

                rejected.append(item)



        return accepted, len(rejected)



    def ask(

        self,

        question: str,

        document_id: int,

        top_k: int = 3,

    ) -> dict:



        if not isinstance(question, str) or not question.strip():

            raise ValueError("question must not be empty")



        if (

            not isinstance(document_id, int)

            or isinstance(document_id, bool)

            or document_id < 1

        ):

            raise ValueError("document_id must be positive")



        if (

            not isinstance(top_k, int)

            or isinstance(top_k, bool)

            or not 1 <= top_k <= 20

        ):

            raise ValueError("top_k must be between 1 and 20")



        search_question = question

        if re.search(r"[\u0600-\u06FF]", question):
            try:
                translated = SearchQueryTranslator().translate(question)
                if translated and not re.search(
                    r"[\u0600-\u06FF]", translated
                ):
                    search_question = translated
            except (ConnectionError, TimeoutError, ValueError, OSError):
                search_question = question

        seeds = self.rag.retrieve(

            question=search_question,

            document_id=document_id,

            top_k=top_k,

        )



        if not seeds:

            return {

                "question": question,

                "document_id": document_id,

                "items": [],

                "source_count": 0,

                "status": "no_context",

            }



        chunks = self.expansion.expand_forward(

            document_id=document_id,

            seed_chunk_ids=[

                chunk["chunk_id"]

                for chunk in seeds

            ],

        )



        if not chunks:

            return {

                "question": question,

                "document_id": document_id,

                "items": [],

                "source_count": 0,

                "status": "no_context",

            }



        result = self.llm.generate(

            question=question,

            chunks=chunks,

        )



        items = result["items"]

        rejected_count = 0



        if self.citation_validator is not None:

            items, rejected_count = self._validate_citations(

                items=items,

                chunks=chunks,

            )





        modality_rejected_count = 0



        if self.modality_guard is not None:

            sources = {

                "S" + str(index): chunk

                for index, chunk in enumerate(chunks, start=1)

            }



            modality_accepted = []



            for item in items:

                source = sources.get(item.get("source_id"))



                if source is None:

                    modality_rejected_count += 1

                    continue



                modality_result = self.modality_guard.evaluate(

                    fact=item["fact"],

                    source_text=source["chunk_text"],

                )



                if modality_result["verdict"] == "PASS":

                    modality_accepted.append(item)

                else:

                    # Fail closed on REJECT, NOT_APPLICABLE,

                    # and any unexpected verdict.

                    modality_rejected_count += 1



            items = modality_accepted



        relevance_rejected_count = 0



        if self.relevance_guard is not None:

            relevant_items = []



            for item in items:

                relevance_result = self.relevance_guard.evaluate(

                    question=question,

                    fact=item["fact"],

                )



                if relevance_result["verdict"] == "RELEVANT":

                    relevant_items.append(item)

                else:

                    relevance_rejected_count += 1



            items = relevant_items



        response = {

            "question": question,

            "document_id": document_id,

            "items": items,

            "source_count": result["source_count"],

            "model": result["model"],

            "status": (

                "answered"

                if items

                else "insufficient_context"

            ),

        }



        if self.citation_validator is not None:

            response["citation_validation"] = {

                "enabled": True,

                "accepted_count": len(items),

                "rejected_count": rejected_count,

                "method": "llm_entailment",

            }





        if self.modality_guard is not None:

            response["modality_validation"] = {

                "enabled": True,

                "accepted_count": len(items),

                "rejected_count": modality_rejected_count,

                "method": "rule_based_modality_guard",

            }



        if self.relevance_guard is not None:

            response["relevance_validation"] = {

                "enabled": True,

                "accepted_count": len(items),

                "rejected_count": relevance_rejected_count,

                "method": "llm_question_relevance",

            }



        return response
