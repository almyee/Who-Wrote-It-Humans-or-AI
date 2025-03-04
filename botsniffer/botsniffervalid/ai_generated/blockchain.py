import hashlib
import time

class Block:
    def __init__(self, index, previous_hash, timestamp, data, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_content = f"{self.index}{self.previous_hash}{self.timestamp}{self.data}{self.nonce}".encode()
        return hashlib.sha256(block_content).hexdigest()

    def mine_block(self, difficulty):
        while self.hash[:difficulty] != "0" * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Block {self.index} mined: {self.hash}")

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4

    def create_genesis_block(self):
        return Block(0, "0", time.time(), "Genesis Block")

    def add_block(self, data):
        prev_block = self.chain[-1]
        new_block = Block(len(self.chain), prev_block.hash, time.time(), data)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

# Testing the blockchain
blockchain = Blockchain()
blockchain.add_block("Transaction 1")
blockchain.add_block("Transaction 2")

for block in blockchain.chain:
    print(vars(block))

