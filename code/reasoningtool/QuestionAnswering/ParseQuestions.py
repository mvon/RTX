import Question
import os, sys
from importlib import reload
reload(Question)
import string
try:
	from code.reasoningtool.QuestionAnswering import WordnetDistance as wd
except ImportError:
	sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
	import WordnetDistance as wd


questions = []
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Questions.tsv'), "r") as fid:
	for line in fid.readlines():
		if line[0] == "#":
			pass
		else:
			questions.append(Question.Question(line))

# The list Questions has elements given by the Question class
# for example, can print the templates
for q in questions:
	print(q.restate_question({}))

# Get the question parameters
print(questions[0].get_parameters("what is dog"))
print(questions[1].get_parameters("What genetic conditions may protect against malaria?"))

# See what happens when it can't extract parameters
print(questions[1].get_parameters("What genetic conditions may protect against asdfasdf?"))

# See how it can restate a question
parameters = questions[1].get_parameters("What genetic conditions may protect against mixed malaria?")
print(questions[1].restate_question(parameters))

# Do the semantic matching, extract the parameters, return the restated question
input_question = "What genetic conditions might offer protection against malaria?"
corpora = [q.corpus for q in questions]
input_question = input_question.strip(string.punctuation)
# Try to pattern match to one of the known queries
(corpus_index, similarity) = wd.find_corpus(input_question, corpora)
parameters = questions[corpus_index].get_parameters(input_question)
print(questions[corpus_index].restate_question(parameters))
