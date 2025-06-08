if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="localhost", port=1111, reload=True)