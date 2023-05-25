import re
import sys
import datetime
from flair.models import SequenceTagger
from flair.data import Sentence
from PySide6 import QtCore, QtWidgets, QtGui

class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # declare widget components
        self.input_file_button = QtWidgets.QPushButton("Choose an input file")
        self.output_file_button = QtWidgets.QPushButton("Choose an output file destination")
        self.updates_text = QtWidgets.QLabel("", alignment=QtCore.Qt.AlignCenter) # used to send status updates to the user
        self.predict_button = QtWidgets.QPushButton("Predict Tags")
        
        # initialize layouts
        self.outer_layout = QtWidgets.QVBoxLayout(self)
        self.file_choice_layout = QtWidgets.QHBoxLayout()

        # put file choice buttons side by side in inner layout
        self.file_choice_layout.addWidget(self.input_file_button)
        self.file_choice_layout.addWidget(self.output_file_button)
        
        # attach inner layout/widets to 
        self.outer_layout.addLayout(self.file_choice_layout)
        self.outer_layout.addWidget(self.updates_text)
        self.outer_layout.addWidget(self.predict_button)
        self.outer_layout.addStretch() # squeeze elements together visually

        # connect buttons to signal slots
        self.input_file_button.clicked.connect(self.set_input_file)
        self.output_file_button.clicked.connect(self.set_output_file)
        self.predict_button.clicked.connect(self.predict_tags)

        # initialize any other variables for this class
        self.tagger_model = None
        self.input_filename = None
        self.output_filename = None

    @QtCore.Slot()
    def set_input_file(self):
        self.input_filename, filter = QtWidgets.QFileDialog.getOpenFileName(self)
        if not self.input_filename:
            self.updates_text.setText("No file was selected")
        else:
            self.updates_text.setText(self.input_filename + " selected")
    
    @QtCore.Slot()
    def set_output_file(self):
        self.output_filename, filter = QtWidgets.QFileDialog.getSaveFileName()
        print(self.output_filename)

    def preprocess_sentence_from_cha(self, line):
        if line[0] == "@": # comments start with @ in .cha
            return
        else:
            try:
                original_text = line.split("*PAR:\t")[1] # our project spec denotes each utterance begins with *PAR:
                preprocessed_text = original_text
                #preprocess out excluded material denoted as <> [e]
                preprocessed_text = re.sub(r'<.*?>\s*\[e\]', '', preprocessed_text)
                # preprocess out pause markers
                if re.search("(\([.]+\))", preprocessed_text):
                    text = ""
                    for part in re.split("(\([.]+\))", original_text):
                        if not re.search("(\([.]+\))", part):
                            text += part[:-1] # [:-1] to strip off extra space from regex splot
                    preprocessed_text = text
                # remove parentheses that fill in incomplete words since the model wasn't trained on this formatting
                while parentheses := re.search("\(.+?\)", preprocessed_text):
                    preprocessed_text = preprocessed_text[0:parentheses.start()] + preprocessed_text[parentheses.start()+1:parentheses.end()-1] + preprocessed_text[parentheses.end():]
                while parentheses := re.search("\<.+?\>", preprocessed_text):
                    preprocessed_text = preprocessed_text[0:parentheses.start()] + preprocessed_text[parentheses.start()+1:parentheses.end()-1] + preprocessed_text[parentheses.end():]
                # preprocess out coded items like &-uh and &=coughs
                preprocessed_text = re.sub(r'&-\w+', '', preprocessed_text)
                preprocessed_text = re.sub(r'&=\w+', '', preprocessed_text)
                # preprocess out anything inside brackets []
                preprocessed_text = re.sub(r'\[[^\]]*\]\s?', '', preprocessed_text)
                # preprocess out @s tags that are sometimes added to code switched text
                preprocessed_text = re.sub(r'@s', '', preprocessed_text)
                # finally, use punctuation to hint removal of timestamps
                preprocessed_text = preprocessed_text.split(".")[0]
                preprocessed_text = preprocessed_text.split("?")[0]
                return preprocessed_text
            except:
                pass # print("failed to parse", line)

    def parse_utterances_from_cha(self):
        utterances = []
        with open(self.input_filename, 'r') as inFile:
            raw_lines = [line for line in inFile]
            i = 0
            while i < len(raw_lines):
                line = raw_lines[i]
                if raw_lines[i][0] == "@":
                    utterances.append(line)
                    i+=1
                elif "*PAR:" in raw_lines[i][:10]: # each utterance by the participant starts with this marker
                    if re.search(r'[0-9]_[0-9]', line):
                        i+=1
                    else:
                        while not re.search(r'[0-9]_[0-9]', line): # CLAN forces a new line on long utterances, the timestamp is at the end of all utterances
                            i+=1
                            line += raw_lines[i]
                    utterances.append(line)
                else:
                    i+=1
        return utterances
    
    @QtCore.Slot()
    def predict_tags(self):
        if not self.input_filename:
            self.updates_text.setText("input and output files must be selected before predicting tags")
            return
        if not self.output_filename:
             self.updates_text.setText("input and output files must be selected before predicting tags")
             return
        if not self.tagger_model:
            self.tagger_model = SequenceTagger.load('./models/gui-model.pt')

        with open(self.output_filename, 'w') as outFile:
            utterances = self.parse_utterances_from_cha()
            for utterance in utterances:
                print("utterance", utterance)
                outFile.write(utterance)
                preprocessed_sentence = self.preprocess_sentence_from_cha(utterance)
                print("preprocessed_sentence", preprocessed_sentence)
                if preprocessed_sentence and len(re.sub(r' ', '', preprocessed_sentence)) != 0:
                    model_sentence = Sentence(preprocessed_sentence)
                    self.tagger_model.predict(model_sentence)
                    outStr = "%pos:"
                    for token in model_sentence:
                        outStr += " " + token.text + "." + token.tag
                    outFile.write(outStr+'\n')
            # write a final comment in the output that it was produced by this tool
            outFile.write("@Comment: %pos tags were generated using the Spanglish-MBERT-CRF-3-Epoch model on " + str(datetime.datetime.now()))
                    

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, widget):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle("Spanglish POS Tagger")

        self.setCentralWidget(widget)

        # handle exit
        exit_action = QtGui.QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_app)

    @QtCore.Slot()
    def exit_app(self, checked):
        QtWidgets.QApplication.quit()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    main_widget = MainWidget()
    
    window = MainWindow(main_widget)
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())