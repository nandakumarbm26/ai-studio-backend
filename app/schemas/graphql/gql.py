import strawberry
from app.schemas.graphql.agent import AgentMutation, AgentQuery
from app.schemas.graphql.auth import AuthMutation, AuthQuery
from app.schemas.graphql.vercelBlobMetaData import VercelBlobMetaDataMutation, VercelBlobMetaDataQuery

@strawberry.type
class Query(AgentQuery, VercelBlobMetaDataQuery, AuthQuery):
    pass

@strawberry.type
class Mutation(AgentMutation, VercelBlobMetaDataMutation, AuthMutation):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)