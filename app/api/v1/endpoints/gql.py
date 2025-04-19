from strawberry.fastapi import GraphQLRouter
from app.schemas.graphql.gql import schema


router = GraphQLRouter(schema)

