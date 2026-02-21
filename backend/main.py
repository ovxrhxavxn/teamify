import uvicorn


def main():

    uvicorn.run(

        app="src.app:app",
        host="192.168.3.37"
    )
if __name__ == "__main__":
    main()