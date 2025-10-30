import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.run_etl import main

if __name__ == "__main__":
    print("Тестируем workflow локально...")
    success = main()
    
    if success:
        print("Workflow тест пройден!")
    else:
        print("Workflow тест не пройден")

