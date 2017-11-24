import numpy as np
np.warnings.filterwarnings('ignore')
import cypher
from collections import namedtuple
from neo4j.v1 import GraphDatabase, basic_auth
import Q1Utils


# Connection information for the neo4j server
driver = GraphDatabase.driver("bolt://lysine.ncats.io:7687", auth=basic_auth("neo4j", "precisionmedicine"))
session = driver.session()

# Connection information for the ipython-cypher package
connection = "http://neo4j:precisionmedicine@lysine.ncats.io:7473/db/data"
DEFAULT_CONFIGURABLE = {
	"auto_limit": 0,
	"style": 'DEFAULT',
	"short_errors": True,
	"data_contents": True,
	"display_limit": 0,
	"auto_pandas": False,
	"auto_html": False,
	"auto_networkx": False,
	"rest": False,
	"feedback": False,  # turn off verbosity in ipython-cypher
	"uri": connection,
}
DefaultConfigurable = namedtuple(
	"DefaultConfigurable",
	", ".join([k for k in DEFAULT_CONFIGURABLE.keys()])
)
config = DefaultConfigurable(**DEFAULT_CONFIGURABLE)

# state space is a tuple (relationship_type, node_label), first order markov chain
def initialize_Markov_chain(connection, config):
	"""
	This initializes an empty Markov chain and returns the transition matrix and state space
	:param connection: ipython-cypher connection string (eg: http://username:password@host.ip/7473/db/data
	:param config: ipython-cypher configuration named tuple
	:return: transition matrix (numpy array) and state space (list of tuples: (rel, node))
	"""
	relationship_types = cypher.run("MATCH ()-[r]-() RETURN DISTINCT type(r)", conn=connection, config=config)
	relationship_types = [item[0] for item in relationship_types]
	node_labels = cypher.run("MATCH (n) RETURN DISTINCT labels(n)[1]", conn=connection, config=config)
	node_labels = [item[0] for item in node_labels]

	# Markov chain will have states = (relationship_label, node_label) since this is a multigraph
	state_space = []
	for relationship_type in relationship_types:
		for node_label in node_labels:
			state = (relationship_type, node_label)
			state_space.append(state)

	#trans_mat = np.zeros((len(state_space), len(state_space)))
	quad_to_matrix_index = dict()
	for state1 in state_space:
		for state2 in state_space:
			quad_to_matrix_index[state1 + state2] = (state_space.index(state1), state_space.index(state2))

	return state_space, quad_to_matrix_index

#state_space, quad_to_matrix_index = initialize_Markov_chain(connection, config)

# Run this on each training example, then normalize
def train(state_space, quad_to_matrix_index, obs_dict, type='ML'):
	"""
	This function will train a Markov chain given a set of observations
	:param trans_mat: current transition matrix
	:param state_space: state space of the Markov chain
	:param type: kind of training to perform (ML=Maximum likelihood, L=Laplace)
	:return: trans_mat
	"""
	trans_mat = np.zeros((len(state_space), len(state_space)))
	omims = obs_dict.keys()
	for omim in omims:
		path_names, path_types = obs_dict[omim]
		for path in path_types:
			tuple_list = []
			for path_index in range(1, len(path)-2+1):
				if path_index % 2 == 1:
					tup = tuple(path[path_index:path_index+2])
					tuple_list.append(tup)
			for tup_index in range(len(tuple_list)-2+1):
				quad = tuple_list[tup_index] + tuple_list[tup_index+1]
				(i, j) = quad_to_matrix_index[quad]
				trans_mat[i, j] += 1
	# Then normalize the thing
	if type == 'ML':
		row_sums = trans_mat.sum(axis=1)
		for index in range(len(row_sums)):
			if row_sums[index] > 0:
				trans_mat[index, :] /= row_sums[index]
	elif type == 'L':
		pseudo_count = 0.01
		trans_mat += pseudo_count  # add a psedo-count
		row_sums = trans_mat.sum(axis=1)
		for index in range(len(row_sums)):
			if row_sums[index] > 0:
				trans_mat[index, :] /= row_sums[index]
	else:
		raise(Exception("Unknown training type:" + str(type)))
	return trans_mat

#trained = train(state_space, quad_to_matrix_index, paths_dict, type='L')

def path_probability(trans_mat, quad_to_matrix_index, path):
	"""
	Computes the probability of a given path
	:param trans_mat: trained transition matrix (numpy matrix)
	:param quad_to_matrix_index: dictionary to keep track of indicies
	:param path: input path of neo4j types
	:return: float representing probability of seeing that path generated by the MArkov chain
	"""
	product = 1
	tuple_list = []
	for path_index in range(1, len(path) - 2 + 1):
		if path_index % 2 == 1:
			tup = tuple(path[path_index:path_index + 2])
			tuple_list.append(tup)
	for tup_index in range(len(tuple_list) - 2 + 1):
		quad = tuple_list[tup_index] + tuple_list[tup_index + 1]
		(i, j) = quad_to_matrix_index[quad]
		product *= trans_mat[i, j]
	return product

#path_probability(trained, quad_to_matrix_index, paths_dict[omim][1][0])

def trained_MC():
	"""
	Trains the Markov chain using known information
	:return: trained transition matrix, dictionary to keep track of indicies
	"""
	known_solutions = dict()
	known_solutions['OMIM:249100'] = 'DOID:2841'
	known_solutions['OMIM:134610'] = 'DOID:2841'
	known_solutions['OMIM:613985'] = 'DOID:12365'
	known_solutions['OMIM:205400'] = 'DOID:12365'
	known_solutions['OMIM:219700'] = 'DOID:1498'

	paths_dict = dict()
	for omim in known_solutions.keys():
		doid = known_solutions[omim]
		path_name, path_type = Q1Utils.interleave_nodes_and_relationships(session, omim, doid, max_path_len=4)
		paths_dict[omim] = (path_name, path_type)
	state_space, quad_to_matrix_index = initialize_Markov_chain(connection, config)
	trained = train(state_space, quad_to_matrix_index, paths_dict, type='L')
	return trained, quad_to_matrix_index

def test():
	paths_dict = dict()
	omim = "test"
	paths_dict[omim] = ([['OMIM:249100',
	'disease_affects',
	'O15553',
	'is_member_of',
	'R-HSA-168643',
	'is_member_of',
	'P01584',
	'gene_assoc_with',
	'DOID:2841']],
	[['omim_disease',
	'disease_affects',
	'uniprot_protein',
	'is_member_of',
	'reactome_pathway',
	'is_member_of',
	'uniprot_protein',
	'gene_assoc_with',
	'disont_disease']])

	state_space, quad_to_matrix_index = initialize_Markov_chain(connection, config)
	trained = train(state_space, quad_to_matrix_index, paths_dict, type='L')
	# This can get messed up if you change the priors
	assert np.abs(path_probability(trained, quad_to_matrix_index, paths_dict[omim][1][0]) - 0.271387803655) < .001
	trained = train(state_space, quad_to_matrix_index, paths_dict, type='ML')
	# This should always == 1
	assert path_probability(trained, quad_to_matrix_index, paths_dict[omim][1][0]) == 1.0