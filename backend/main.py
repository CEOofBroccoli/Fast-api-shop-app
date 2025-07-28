from fastapi import FastAPI

app = FastAPI(title="Inventory Management System")

@app.get("/")
def root():
    return {"message": "Inventory Management System API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}