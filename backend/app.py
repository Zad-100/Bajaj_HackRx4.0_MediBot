# Backend for Medibot


# Flask imports
from flask import Flask, jsonify, request
from flask_cors import CORS

# Langchain imports
from langchain.embeddings import TensorflowHubEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain import OpenAI
from langchain.prompts import PromptTemplate
from langchain import HuggingFaceHub

# ChromaDB imports
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# Other imports
import os
from dotenv import load_dotenv, find_dotenv
from io import BytesIO
import pickle

# Set up Flask App
app = Flask(__name__)
CORS(app, origins='*')

print("loading environment variables...")
_ = load_dotenv(find_dotenv()) # read local .env file

print("downloading chromadb emeddings from cloud, please wait...")
chromadb_embeddings = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

print("loading langchain emeddings...")
langchain_embeddings = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

print("loading AWS deployed ChromaDB Stack environment variables...")
CHROMA_HOST = os.getenv('CHROMA_HOST')
CHROMA_PORT = os.getenv('CHROMA_PORT')
COLLECTION_NAME=os.getenv('COLLECTION_NAME')

# Setup chroma settings
chroma_client_settings = Settings(
        chroma_api_impl="rest",
        chroma_server_host=CHROMA_HOST,
        chroma_server_http_port=CHROMA_PORT,
    )

# Set up chroma client settings
chroma_client = chromadb.HttpClient(host="15.206.208.236", port="8000")
print("ChromaDB's heartbeat: ", chroma_client.heartbeat())

# Set up Chroma collection
collection = chroma_client.get_collection(name=COLLECTION_NAME,
                                        embedding_function=chromadb_embeddings)
print("collection counts: ", collection.count())

# Set up langchain vectorDB
vectordb = Chroma(client=chroma_client,client_settings=chroma_client_settings,
                  collection_name=COLLECTION_NAME,
                  embedding_function=langchain_embeddings)
print("set up vectordb")

# Initialise some important lists
trigger_words = ["suicide", "kill myself", "end my life", "can't go on",
                 "no reason to live"]
diseases_list =['coronavirus', 'influenza', 'common cold',
                'respiratory syncytial virus', 'pneumonia',
                'severe acute respiratory syndrome',
                'respiratory tract infections',
                'middle east respiratory syndrome']

class Session:
    """Template class for a session with the chatbot"""
    def __init__(self):
        self.chroma_client = chroma_client
        self.collection = collection
        self.vectordb = vectordb

class User_Session(Session):
    """Class to manage one user session on the chatbot platform"""
    def __init__(self):
        Session.__init__(self)
        self.selected_llm ="OpenAI"
        self.selected_nlp=False
        self.query = ""
        self.query_intent=""
        self.query_disease=""
        self.validDisease=False
        self.sources = []
        self.chat_history = []
        self.responses = []
        self.source_ids = ""
        self.source_cites = []
        self.rating = 5 # initalise every content with 5 star

    def get_llm(self):
        """Load the LLM from langchain; default LLM is OpenAI"""
        if self.selected_llm == "Google-Flan-T5-XXL":
            llm = HuggingFaceHub(repo_id='google/flan-t5-xxl',
                                 model_kwargs={"temperature":0.1,
                                               "max_new_tokens":1180})
        elif self.selected_llm == "OpenAssistant":
            llm = HuggingFaceHub(repo_id="OpenAssistant/oasst-sft-1-pythia-12b",
                                 model_kwargs={"temperature":0.1,
                                               "max_new_tokens":768})
        elif self.selected_llm == "Falcon-7b-instruct":
            llm = HuggingFaceHub(repo_id="tiiuae/falcon-7b-instruct",
                                 model_kwargs={"temperature":0.1,
                                               "max_new_tokens":256})
        else:
            llm = OpenAI()
        return llm
    
    def isValidDisease(self):
        """Check if disease in diseases list"""
        # print("inside isValidDisease")
        if (self.query_disease in diseases_list) or ("No disease".lower() in self.query_disease.lower()):
            self.validDisease = True
        elif self.query_disease not in diseases_list:
            print("checking mapping...")

            # Map it with any disease from disease list
            llm = self.get_llm()
            mappingTemplate = """The following is a disease given along with a \
list of diseases. Give answer as ONLY True or False if the disease maps to any \
of the disease from the list
            disease: {disease}
            disease list: {diseases_list} 
            """
            mappingPrompt = PromptTemplate(input_variables=['disease','diseases_list'], template=mappingTemplate)
            mappingChain = LLMChain(llm=llm, prompt=mappingPrompt)
            response = mappingChain.run(disease=self.query_disease,
                                        diseases_list=diseases_list)
            if "True" in response:
                self.validDisease = True
        print(self.validDisease)

    # Intent using LLM
    def get_llm_intent(self):
        """Determine the intent of the user's prompt using LLM"""
        llm = self.get_llm()
        template = "The following is given query from a user. Apply NLP and identify the intent only from the following choices: ['Symptom Inquiry', 'Treatment Enquiry', 'Medical Information', 'Medical Advice', 'Non-medical queries']. User query: {query}"
        intentPrompt = PromptTemplate(input_variables=['query'],
                                      template=template)
        IntentChain = LLMChain(llm =llm, prompt=intentPrompt)
        self.query_intent = IntentChain.run(query = self.query)
        self.query_intent = self.query_intent[2:]
        print(self.query_intent)

    # Intent using custom trained model
    def get_nlp_intent(self):
        """Determine the intent of the user's prompt using custom made model"""
        with open('custom_trained_models\intentClassifierModel0.pkl','rb') as file:
            loaded_model = pickle.load(file)

        self.query_intent = loaded_model.predict([self.query])[0]
        print(self.query_intent)

    # Disease determination using LLM
    def get_llm_disease(self):
        """Extract the disease in the user's prompt using LLM"""
        llm = self.get_llm()
        template ="From the given query, identify if it mentions any disease and return only that disease. If no disease is mentioned only say 'No disease' exactly. User query: {query}"

        diseasePrompt = PromptTemplate(input_variables=['query'],
                                       template=template)
        diseaseChain = LLMChain(llm =llm, prompt=diseasePrompt)
        self.query_disease = diseaseChain.run(query = self.query)
        self.query_disease = self.query_disease[2:]
        # print("Moving to isValidDisease")
        self.isValidDisease()
        print(self.query_disease)

    # Disease using custom trained model
    def get_nlp_disease(self):
        """Extract disease using custom trained model"""
        with open('custom_trained_models\extractDiseaseModel0.pkl','rb') as file:
            loaded_model = pickle.load(file)

        self.query_disease = loaded_model.predict([self.query])[0]
        self.isValidDisease()
        print(self.query_disease)

    def response_from_llm(self):
        """Generate response from the LLM loaded"""
        llm = self.get_llm()
        self.response = ""
        self.source_id = ""
        self.source_cites = []
        self.chat_history = []
        
        # First we get the best response out of all the sources based on the
        # selected sources
        # We need to create the search_kwargs filter
        # We create the or_filter from all the sources
        or_filters =[]
        for source in self.sources:
            source_dict = {'source':source}
            or_filters.append(source_dict)
        
        # Define search kwargs
        search_kwargs = {
                'k':1,
                'filter':{
                    "$and": [
                        {
                            "$or": or_filters
                        },
                        {
                            "rating": {'$gt': 4}
                        }
                    ]
                }
            }
        
        # Define template for taking into consideration query_intent
        intentTemplate = '''Given the following conversation, a follow up \
question, and its intent, rephrase the follow up question to be a standalone question.
        Chat History:
        {chat_history}
        Follow Up Input: {question}
        Question Intent: {intent}
        Standalone question:'''
        
        # define promptTemplate
        prompt = PromptTemplate(input_variables=['chat_history',
                                                 'question','intent'],
                                                 template = intentTemplate)

        # Define retrieval chain
        qa = ConversationalRetrievalChain.from_llm(llm = llm,
                                    retriever = self.vectordb.as_retriever(),
                                    return_source_documents = True,
                                    condense_question_prompt=prompt)

        # Get the response
        result = qa({'question':self.query, "chat_history":self.chat_history,
                     "intent":self.query_intent})
        self.response = result['answer']
        if self.response == " I don't know":
            return self.response, "None"
        target_document = result['source_documents'][0]
        print(target_document.metadata['source'])

        # Self.source_cites.append(target_document.metadata['url'])
        
        self.source_id = self.collection.query(
            query_texts=target_document.page_content, n_results=1
        )['ids'][0][0]

        # print(len(self.vectordb.get(where={"rating": {'$gt': 4}})['ids']))

        for source in self.sources:
            document = self.vectordb.similarity_search(self.query, k=1,
                                                       filter={
                'source':source
            })
            self.source_cites.append(document[0].metadata['url'])
        
        return self.response, self.source_cites
    
    def update_rating(self):
        """Update the rating of a particular doc retrieved"""
        
        # Get the document with
        # ids == self.source_ids[0] :: this returns a dictionary
        doc = self.vectordb.get(ids=[self.source_id])
        
        # Get the current rating of the article
        curr_rating = doc['metadatas'][0]['rating']

        # Update the rating
        new_rating = (curr_rating + self.rating) / 2
        doc['metadatas'][0]['rating'] = new_rating
        
        # Create a langchain document from dictionary
        document =Document(
            ids=doc['ids'][0],
            page_content=doc['documents'][0],
            metadata={
                'source': doc['metadatas'][0]['source'],
                'url': doc['metadatas'][0]['url'],
                'disease': doc['metadatas'][0]['disease'],
                'rating': doc['metadatas'][0]['rating'],
            }
        )

        # Update the vectordb
        self.vectordb.update_document(self.source_id, document)
        #print(len(self.vectordb.get(where={"rating": {'$gt': 4}})['ids']))
        
class Admin_Session(Session):
    """Child class to manage Admin Sessions on chatbot"""
    def __init__(self):
        Session.__init__(self)
        self.file = None
        self.fileName = ""
        self.fileContent = ""

    def create_document(self):
        """Convert file to document that can be added to ChromaDB"""
        # print("Inside the function")
        print(self.fileContent)

        # Apply in the ChromaDB's Schema
        document = Document(
            page_content = self.fileContent,
            metadata = {
                'source': self.fileName,
                'url': None,
                'disease': 'Generic',
                'rating': 5
            }
        )
        # print("This is the document: ", document)

        # Chunk the document
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=20
        )

        documents = text_splitter.split_documents([document])
        print("chunks of documents created successfully")
        
        return documents
    
    def add_document_to_vectordb(self, doc):
        """Add document to ChromaDB"""  
        print("inside adding the document function")
        print(doc)
        print(doc.metadata)
        print(type(doc.metadata))
        self.collection.add(
            ids=str(collection.count()+1),
            documents=doc.page_content,
            metadatas = doc.metadata
        )
        print("The count of the collection in ChromaDB: ", collection.count())

# Create user instance for user session
user = User_Session()

# Add sources for filtering
@app.route("/upload_sources", methods=['POST'])
def upload_sources():
    """Add sources for filtering the responses"""
    uploadStatus = {}
    try:
        user.sources.append(request.json['source'])
        print(user.sources)
        uploadStatus['status'] = 1

    except Exception as e:
        print(f"Couldn't upload source {e}")
        uploadStatus['status'] = 0

    return jsonify(uploadStatus)

@app.route("/remove_sources", methods=['POST'])
def remove_sources():
    """Remove sources if user disabled the source"""
    removeStatus = {}
    try:
        user.sources.remove(request.json['source'])
        print(user.sources)
        removeStatus['status'] = 1

    except Exception as e:
        print(f"Couldn't remove source {e}")
        removeStatus['status'] = 0

    return jsonify(removeStatus)

@app.route("/select_llm", methods=['POST'])
def select_query_llm():
    """(ONLY FOR PITCHING) Select the LLM to use for querying and summarising"""
    selectionStatus = {}
    try:
        user.selected_llm = request.json['selected_llm']
        print(user.selected_llm)
        selectionStatus['status'] = 1

    except Exception as e:
        print(f"Couldn't set preferred llm {e}")
        selectionStatus['status'] = 0

    return jsonify(selectionStatus)

# Select whether to perform Intent Entityt Classification using NLP or not
@app.route("/select_nlp", methods=['POST'])
def select_nlp():
    """Choose if NLP model to use to perform intent classification"""
    nlpStatus = {}
    try:
        user.selected_nlp = True
        print(user.selected_nlp)
        nlpStatus['status'] = 1

    except Exception as e:
        print(f"Couldn't set for nlp method {e}")
        nlpStatus['status'] = 0

    return jsonify(nlpStatus)

@app.route("/patient_query", methods=['POST'])
def patient_query():
    """Endpoint to upload the patient query"""
    uploadStatus = {}
    try:
        user.query = request.json['query']
        print(user.query)
        # Get the intent from the query
        print(user.selected_nlp)
        if(user.selected_nlp == True):
            user.get_nlp_intent()
            if user.query_intent != "Non-medical Queries":
                user.get_nlp_disease()
        else:
            user.get_llm_intent()
            if user.query_intent != "Non-medical Queries":
                user.get_llm_disease()
        uploadStatus['status'] = 1

    except Exception as e:
        print(f"Couldn't upload query {e}")
        uploadStatus['status'] = 0

    return jsonify(uploadStatus)

@app.route("/run_medibot", methods=['GET'])
def run_medibot():
    """Generate response for the patient query."""
    response = ""

    # Check for intent
    print(user.query_intent)
    if user.query_intent == "Non-medical queries":
        response = "This is a non-medical query"
        source_cites = "None"
    elif user.validDisease == False:
        response = "This disease is not currently in our database"
        source_cites = "None"
    # Check for trigger words
    elif any(word in user.query.lower() for word in trigger_words):
        response = "I'm really sorry that you're feeling this way, but I'm unable to provide the help that you need. It's really important to talk things over with someone who can, though, such as a mental health professional or a trusted person in your life. Contact: Helpline KIRAN (1800-599-0019)"
        source_cites ="None"
    
    elif len(user.sources) == 0:
        response = 'No sources selected'
        source_cites = "None"
        print(response)
    else:
        response, source_cites = user.response_from_llm()
        if(response == " I don't know."):
            response = "Please ask me medical queries only."
            source_cites = "None"
        print(response)
        return jsonify({
            'response' : response,
            'source_cites':source_cites
            })
    return jsonify({'response': response})
    
@app.route("/feedback", methods=['POST'])
def feedback():
    """
        Function to take user feedback to update the retrieved information's
        ranking
    """
    uploadStatus = {}
    try:
        user.rating = request.json['rating']
        print(user.rating)
        user.update_rating()
        uploadStatus['status'] = 1

    except Exception as e:
        print(f"Couldn't upload query {e}")
        uploadStatus['status'] = 0

    return jsonify(uploadStatus)

# For admin page
@app.route("/admin_vectordb", methods=['POST'])
def admin_vectordb():
    """Function to add private knowledge base to the vector database"""
    admin = Admin_Session()

    uploadStatus = {}
    try:
        print('Started...')
        admin.file = request.files['file']
        admin.fileName = admin.file.filename
        print(f"Uploading file {admin.fileName}")

        file_bytes = admin.file.read()
        fileObj = BytesIO(file_bytes)
        print("converted to fileobj")
        print(type(fileObj))
        fileObj.seek(0)
        admin.fileContent = fileObj.read()
        
        print("Read from fileobj")
        print(type(admin.fileContent))
        print(admin.fileContent)

        admin.fileContent = str(admin.fileContent)
        print("converted to string ig")
        print(type(admin.fileContent))

        documents = admin.create_document()
        
        # Add documents to the vector database
        for doc in documents:
            admin.add_document_to_vectordb(doc)

        uploadStatus['status'] = 1

    except Exception as e:
        print(f"Couldn't upload document {e}")
        uploadStatus['status'] = 0

    return jsonify(uploadStatus)


# Run the app
if __name__ == '__main__': 
    app.run(debug=True)