# This Is the Problem HNSW Solves

# HNSW helps Qdrant answer this question:

#     "How can I find almost the best result without checking every vector?"
# HNSW builds a graph that connects similar vectors together.

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Range
from sentence_transformers import SentenceTransformer
from qdrant_client.models import Filter, FieldCondition, MatchValue

model = SentenceTransformer("all-MiniLM-L6-v2")
# vector = model.encode("This is a sample point for triage practice.")
client = QdrantClient(host="localhost", port=6333)
# 8 payloa indexining means , if w want to search anything in a olltion an where
#  is alot of hunks (points an every point has payloa) so instea of checking every
# payload it we give it index so it fast our search process, and we choose index from payload value i-e year, author, etc but it should not be tile or sumamry
# creating index
# Let's create an index on the department field.
from qdrant_client.models import PayloadSchemaType

client.create_payload_index(  # this tell Qdrant Create an index for a payload field.
    collection_name="documents",
    field_name="department",  # Which payload field?
    field_schema=PayloadSchemaType.KEYWORD,  # it define that the key word is an KEYWORD, OR INTEGER,ORFLOAT ETC MEANS DEFINE THE DATATYPE
)

# 9. Quantization?
# means Represent numbers using fewer bits while preserving most of the useful information.
# scaler quantization: become the number short e.g if we have 0.9264747 it make it 0.92 and it does not effect embedding .else
# product quantization: is advance it convert the embedding into groups and them compress it
#  e.g we have 768 it make groups like 98,98,98 etc and then compress each group
from qdrant_client.models import ScalarQuantization, ScalarQuantizationConfig

# Simplified conceptual example
quantization_config = ScalarQuantization(scalar=ScalarQuantizationConfig())

# 8. multi vector we are making multi vector in one point beause if we have a product and we want store their embedding in one vector so it missed some information thats why
#  we will be using multiple vectore of a product e.g title embedding, description embedding, image embedding
# so if user search on tile, or description or image they well get the same point.

from qdrant_client.models import VectorParams, Distance

client.create_collection(
    collection_name="articles",
    vectors_config={
        "title": VectorParams(size=384, distance=Distance.COSINE),
        "content": VectorParams(size=768, distance=Distance.COSINE),
    },
)
# insrting data at multi vtor.
client.upsert(
    collection_name="articles",
    points=[
        {
            "id": 1,
            "vector": {"title": [0.2, 0.4, 0.8], "content": [0.5, 0.1, 0.7]},
            "payload": {"title": "Python"},
        }
    ],
)

# 7 Crud opearation
# read from qdrant
client.retrieve(collection_name="traigeflow practice", ids=[1])
# for inser and delete we use client.upsert()
# as we did below

# delete
from qdrant_client.models import PointIdsList

client.delete(
    collection_name="books",
    # PointIdsList means a list of ids to delete e.g,points = [3,7,8,2] etc
    points_selector=PointIdsList(points=[3]),
)

# Batcg insetrt.
# should we do upsert ,upsert( 10000pdf if we have?.)

# 6. now lets combine search and filtering
results = client.query_points(
    collection_name="books",
    query=query_vector.tolist(),
    query_filter=Filter(
        must=[FieldCondition(key="language", match=MatchValue(value="English"))]
    ),
    limit=5,
)
# 5. filter
# suppose we have this payload
# payload = {
#     "title": "Python Basics",
#     "author": "John",
#     "year": 2024,
#     "category": "Programming",
#     "language": "English"
# }

filter = Filter(  # This creates a filter object.
    # must means These conditions must be true.
    must=[
        # fieldcondition means Look at one field inside the payload.
        FieldCondition(
            # key="language"
            key="language",
            # means MatchValue means Compare the value exactly.
            # Onlypoint where language == english
            match=MatchValue(value="english"),
        )
    ],
    # another filter which is " should"
    # means Either one is acceptable. Think of it as a logical OR.
    # another filter which strictly not be allowed
    # must_not: this is the filter object
)

#  Range filter we cam define range here e.g from 2003 to 2004 or after 2023 etc.
FieldCondition(
    key="year",
    range=Range(gt=2023),  # gt meabs greater than more like lte, ge, gte,lte etc
)
# combining multiple condition
Filter(
    must=[
        FieldCondition(key="category", match=MatchValue(value="Programming")),
        FieldCondition(key="year", range=Range(gt=2023)),
    ]
)
# 4. search in a collection
vector_for_search = model.encode("this traige flow practice")

result = client.query_points(
    collection_name="traigeflow",
    query=vector_for_search.tolist(),
    limit=5,  # it means return only five results
)
# print result
for point in result.points:
    print(f"Point ID: {point.id}, Payload: {point.payload}, Score: {point.score}")
    print(" the whole point is ", point)

# 3. point insertion
point_insert = client.upsert(
    collection_name="triage-practice",
    points=[
        PointStruct(
            id=1,
            # vector=vector.tolist(),
            vector=[0.1] * 768,  # Example vector;
            payload={
                "name": "Adnan Khan",
                "age": 30,
                "text": "This is a sample point for triage practice.",
            },
        )
    ],
)
# 2. point making
point = PointStruct(
    id=1,
    # vector=vector.tolist(),
    vector=[
        0.1,
    ]
    * 768,  # Example vector; replace with actual vector from model.encode()
    payload={"text": "This is a sample point for triage practice."},
)

1.0  # collection making
client.create_collection(
    collection_name="triage-practice",
    vectors_config=VectorParams(
        size=768, distance=Distance.COSINE
    ),  # describes the vector configuration for the collection.
)
