import pinecone
from typing import List, Tuple, Optional


class PineconeClient:
    def __init__(self, api_key: str, environment: str, index_name: str, dimension: int):
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.dimension = dimension

        # Initialize Pinecone
        pinecone.init(api_key=self.api_key, environment=self.environment)

        # Create index if it doesn't exist
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(self.index_name, dimension=self.dimension)

        # Connect to the index
        self.index = pinecone.Index(self.index_name)

    def upsert_vectors(self, vectors: List[Tuple[str, List[float]]]):
        """
        Upserts a list of (id, vector) tuples to the index.
        """
        return self.index.upsert(vectors=vectors)

    def query_vector(self, vector: List[float], top_k: int = 5, include_metadata: bool = True):
        """
        Queries the index for the top_k most similar vectors.
        """
        return self.index.query(vector=vector, top_k=top_k, include_metadata=include_metadata)

    def delete_vectors(self, ids: List[str]):
        """
        Deletes vectors with the specified IDs from the index.
        """
        return self.index.delete(ids=ids)

    def fetch_vectors(self, ids: List[str]):
        """
        Fetches vectors by IDs.
        """
        return self.index.fetch(ids=ids)

    def update_vector(self, id: str, values: List[float]):
        """
        Updates a vector for the given ID.
        """
        return self.index.update(id=id, values=values)

    def describe_index(self):
        """
        Returns the index description.
        """
        return pinecone.describe_index(self.index_name)

    def delete_index(self):
        """
        Deletes the index completely.
        """
        pinecone.delete_index(self.index_name)
