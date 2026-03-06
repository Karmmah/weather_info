#!/usr/bin/env python3

def main():
    stuff = ""
    while stuff != "close":
        stuff = input()
        #print(f"print: {stuff}")
        print(f"print: {stuff}", flush=True)
    print("CLOSED")

if __name__ == "__main__":
    print("STARTED")
    main()
