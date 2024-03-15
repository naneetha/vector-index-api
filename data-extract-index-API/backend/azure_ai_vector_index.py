from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from backend.config import *
import dotenv

from azure.search.documents.models import (
    QueryAnswerType,
    QueryCaptionType,
    QueryCaptionResult,
    QueryAnswerResult,
    SemanticErrorMode,
    SemanticErrorReason,
    SemanticSearchResultsType,
    QueryType,
    VectorizedQuery,
    VectorQuery,
    VectorFilterMode,    
)
from azure.search.documents.indexes.models import (  
    ExhaustiveKnnAlgorithmConfiguration,
    ExhaustiveKnnParameters,
    SearchIndex,  
    SearchField,  
    SearchFieldDataType,  
    SimpleField,  
    SearchableField,  
    SearchIndex,  
    SemanticConfiguration,  
    SemanticPrioritizedFields,
    SemanticField,  
    SearchField,  
    SemanticSearch,
    VectorSearch,  
    HnswAlgorithmConfiguration,
    HnswParameters,  
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
    VectorSearchAlgorithmKind,
    VectorSearchProfile,
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    ExhaustiveKnnParameters,
    SearchIndex,  
    SearchField,  
    SearchFieldDataType,  
    SimpleField,  
    SearchableField,  
    SearchIndex,  
    SemanticConfiguration,  
    SemanticField,  
    SearchField,  
    VectorSearch,  
    HnswParameters,  
    VectorSearch,
    VectorSearchAlgorithmKind,
    VectorSearchAlgorithmMetric,
    VectorSearchProfile,
)  

dotenv.load_dotenv()


def create_vector_index(index_name,semantic_index_name):
    # Configure the vector search configuration  
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="myHnsw",
                kind=VectorSearchAlgorithmKind.HNSW,
                parameters=HnswParameters(
                    m=4,
                    ef_construction=400,
                    ef_search=500,
                    metric=VectorSearchAlgorithmMetric.COSINE
                )
            ),
            ExhaustiveKnnAlgorithmConfiguration(
                name="myExhaustiveKnn",
                kind=VectorSearchAlgorithmKind.EXHAUSTIVE_KNN,
                parameters=ExhaustiveKnnParameters(
                    metric=VectorSearchAlgorithmMetric.COSINE
                )
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="myHnswProfile",
                algorithm_configuration_name="myHnsw",
            ),
            VectorSearchProfile(
                name="myExhaustiveKnnProfile",
                algorithm_configuration_name="myExhaustiveKnn",
            )
        ]
    )
    semantic_config = SemanticConfiguration(
        name=AZURE_SEARCH_SEMANTIC_CONFIG_NAME,
        prioritized_fields=SemanticPrioritizedFields(
            content_fields=[SemanticField(field_name="content")]
        )
    )
    # Create the semantic settings with the configuration
    semantic_search = SemanticSearch(configurations=[semantic_config])

    #Create Search Index client
    search_client = SearchIndexClient(AZURE_SEARCH_SERVICE_ENDPOINT, AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY))
    
    # Create the index    
    fields = [
            SimpleField(name="documentId", type=SearchFieldDataType.String, filterable=True, sortable=True, key=True),     
            SearchableField(name="content", type=SearchFieldDataType.String),        
            SearchField(name="embedding", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True, vector_search_dimensions=1536, 
                    vector_search_profile_name="myHnswProfile"),
            SimpleField(name="filepath", type=SearchFieldDataType.String, filterable=True, Facetable=True)  
        ]

    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_search
        )
    # Create the search index with the semantic settings
    semantic_index = SearchIndex(name=semantic_index_name, fields=fields,
                      vector_search=vector_search, 
                      semantic_search=semantic_search)
    
    semantic_result = search_client.create_or_update_index(semantic_index)
    result = search_client.create_or_update_index(index)

    print(f' Index with name {result.name} and {semantic_result.name} created')
