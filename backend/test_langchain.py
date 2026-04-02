from langchain_ollama import OllamaLLM

# connect to ollama
llm = OllamaLLM(
    model="mistral:7b",
    base_url="http://49.204.233.77:11434"
)

# input
question = input("Ask something: ")

response = llm.invoke(question)

print("\nAI Response:\n", response)