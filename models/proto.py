from transformers import LineByLineTextDataset, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
data = LineByLineTextDataset(
    tokenizer=tokenizer,
    file_path='./pretraining.corpus',
    block_size=128
)

print(data)