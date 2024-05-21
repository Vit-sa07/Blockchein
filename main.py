import hashlib  # Импортируем библиотеку для работы с хэш-функциями
import struct  # Импортируем библиотеку для работы с бинарными данными
import time  # Импортируем библиотеку для работы со временем


# Функция для вычисления SHA-256 Эта функция принимает данные, вычисляет их хэш с использованием алгоритма SHA-256 и
# возвращает его в виде строки шестнадцатеричных цифр.
def sha256(data):
    return hashlib.sha256(data).hexdigest()


# Функция для вычисления корня дерева Меркла
# Эта функция принимает список хэшей транзакций и рекурсивно вычисляет корневой хэш дерева Меркла.
def merkle_root(transactions):
    # Если список содержит только один элемент, он и есть корень
    if len(transactions) == 1:
        return transactions[0]

    new_level = []
    # Обрабатываем список пар элементов
    for i in range(0, len(transactions), 2):
        if i + 1 < len(transactions):
            # Если пара существует, хэшируем её вместе
            new_level.append(sha256(bytes.fromhex(transactions[i]) + bytes.fromhex(transactions[i + 1])))
        else:
            # Если пары нет, дублируем последний элемент и хэшируем его с самим собой
            new_level.append(sha256(bytes.fromhex(transactions[i]) + bytes.fromhex(transactions[i])))

    # Рекурсивно вызываем функцию для нового уровня
    return merkle_root(new_level)


# Функция для создания заголовка блока Эта функция принимает хэш предыдущего блока, корневой хэш дерева Меркла и
# nonce, и возвращает заголовок блока в виде бинарных данных.
def create_block_header(prev_hash, merkle_root_hash, nonce):
    version = struct.pack("<L", 1)  # Устанавливаем версию блока (4 байта)
    prev_block_hash = bytes.fromhex(prev_hash)  # Преобразуем хэш предыдущего блока из строки в байты (32 байта)
    merkle_root = bytes.fromhex(merkle_root_hash)  # Преобразуем корневой хэш дерева Меркла из строки в байты (32 байта)
    timestamp = struct.pack("<L", int(time.time()))  # Получаем текущее время и упаковываем его в 4 байта
    bits = struct.pack("<L", 0x1d00ffff)  # Устанавливаем текущую цель сложности сети (4 байта)
    nonce = struct.pack("<L", nonce)  # Упаковываем nonce в 4 байта
    return version + prev_block_hash + merkle_root + timestamp + bits + nonce


# Функция для майнинга блока
# Эта функция изменяет nonce до тех пор, пока не найдет хэш заголовка блока, который начинается с четырех нулей.
def mine_block(prev_hash, merkle_root_hash):
    nonce = 0
    while True:
        # Создаем заголовок блока
        block_header = create_block_header(prev_hash, merkle_root_hash, nonce)
        # Вычисляем хэш заголовка блока
        block_hash = sha256(block_header)
        # Проверяем, начинается ли хэш с четырех нулей
        if block_hash.startswith("0000"):
            # Если да, возвращаем хэш блока и nonce
            return block_hash, nonce
        # Увеличиваем nonce и продолжаем поиск
        nonce += 1


# Основная функция
def main():
    # Считывание данных из файлов транзакций
    transactions = []
    for i in range(1, 5):
        # Открываем файл с транзакцией и читаем его содержимое
        with open(f"transaction{i}.txt", "rb") as f:
            transaction = f.read()
            # Вычисляем хэш транзакции и добавляем его в список
            transactions.append(sha256(transaction))

    # Подсчет корня дерева Меркла
    root_hash = merkle_root(transactions)
    print("Корневой хеш Меркла:", root_hash)

    # Считывание хэша заголовка предыдущего блока из файла
    with open("prev_block_hash.txt", "r") as f:
        prev_block_hash = f.read().strip()

    # Майнинг блока
    block_hash, nonce = mine_block(prev_block_hash, root_hash)
    print("Block Hash:", block_hash)
    print("Nonce:", nonce)

    # Создание заголовка блока
    block_header = create_block_header(prev_block_hash, root_hash, nonce)

    # Сохранение блока в файл
    with open("block.bin", "wb") as f:
        f.write(block_header)


if __name__ == "__main__":
    main()
