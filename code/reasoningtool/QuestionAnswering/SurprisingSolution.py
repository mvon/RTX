
import os
import sys
import argparse
# PyCharm doesn't play well with relative imports + python console + terminal
try:
	from code.reasoningtool import ReasoningUtilities as RU
except ImportError:
	sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
	import ReasoningUtilities as RU

import FormatOutput
import networkx as nx
try:
	from QueryCOHD import QueryCOHD
except ImportError:
	sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
	try:
		from QueryCOHD import QueryCOHD
	except ImportError:
		sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kg-construction'))
		from QueryCOHD import QueryCOHD

from COHDUtilities import COHDUtilities

import CustomExceptions


class SurprisingSolution:

	def __init__(self):
		None

	@staticmethod
	def answer(drug_id, use_json=False, num_show=20, rev=True, conservative=True):
		"""
		Answers the question 'What conditions appear less often than expected when taking $chemical_substance?'
		:param drug_id: KG drug node curie id
		:param use_json: bool, use JSON output
		:param num_show: int, number to display
		:param rev: bool. If true - order by most likely contraindicated
		:param conservative: bool, True if using exact matches, False if using any synonyms returned by COHD
		:return: none
		"""

		# Initialize the response class
		response = FormatOutput.FormatResponse(6)

		# get the description
		drug_description = RU.get_node_property(drug_id, 'name')

		# Get the conditions that COHD says it's used to treat
		conditions_treated = COHDUtilities.get_surprising_conditions_treating(drug_description, conservative=conservative)

		# sort the diseases by frequency
		ids_counts = []
		for id in conditions_treated:
			cond = conditions_treated[id]
			ids_counts.append((id, cond['ln_ratio']))

		# filter oposite examples
		if rev:
			ids_counts = [x for x in ids_counts if x[1] > 0]
			more_less = "more"
			edge_indication = "contraindicates"
		else:
			ids_counts = [x for x in ids_counts if x[1] < 0]
			more_less = "less"
			edge_indication = "indicates"


		if len(ids_counts) == 0:
			error_message = "Sorry, Columbia Open Health Data has no examples of diseases observed significantly %s than expected in patients treated with %s" % (more_less, drug_description)
			error_code = "EmptyResult"
			response.add_error_message(error_code, error_message)
			response.print()
			return 1


		#ids_counts_sorted = sorted(ids_counts, key=lambda x: x[1], reverse=rev)
		ids_counts_sorted = ids_counts
		ids_counts_sorted.sort(reverse=rev, key=lambda x: x[1])
		ids_sorted = [i[0] for i in ids_counts_sorted]

		# reduce to top n
		ids_sorted_top_n = ids_sorted
		if len(ids_sorted_top_n) > num_show:
			ids_sorted_top_n = ids_sorted_top_n[0:num_show]

		# return the results
		if not use_json:
			if rev:
				to_print = "The most likely conditions for contraindication "
			else:
				to_print = "The most likely conditions for indication "
			to_print += "with %s, according to the Columbia Open Health Data, are:\n" % drug_description
			for id in ids_sorted_top_n:
				to_print += "condition: %s\t count %d \t log ratio %f \n" % (conditions_treated[id]['concept_2_name'], conditions_treated[id]['observed_count'], conditions_treated[id]['ln_ratio'])
			print(to_print)
		else:
			#  otherwise, you want a JSON output
			#  Attempt to map the COHD names to the KG (this takes some time)l. TODO: find further speed improvements
			drug_as_graph = RU.get_node_as_graph(drug_id)
			drug_node_info = list(drug_as_graph.nodes(data=True))[0][1]
			id_to_KG_name = dict()
			id_to_name = dict()
			id_to_count = dict()
			id_to_frequency = dict()
			id_to_id = dict()

			# Map ID's to all relevant values
			for id in ids_sorted_top_n:
				id_to_name[id] = conditions_treated[id]['concept_2_name']
				id_to_count[id] = conditions_treated[id]['observed_count']
				id_to_frequency[id] = conditions_treated[id]['ln_ratio']
				id_to_KG_name[id] = None
				#print(QueryCOHD.get_xref_from_OMOP(id, "DOID, OMIM, HP"))
				try:
					id_to_KG_name[id] = RU.get_id_from_property(id_to_name[id], 'name', label="phenotypic_feature")
					if id_to_KG_name[id] is None:
						assert False
					id_to_id[id_to_KG_name[id]] = id
				except:
					try:
						id_to_KG_name[id] = RU.get_id_from_property(id_to_name[id], 'name', label="disease")
						if id_to_KG_name[id] is None:
							assert False
						id_to_id[id_to_KG_name[id]] = id
					except:
						try:
							id_to_KG_name[id] = RU.get_id_from_property(id_to_name[id].lower(), 'name', label="phenotypic_feature")
							if id_to_KG_name[id] is None:
								assert False
							id_to_id[id_to_KG_name[id]] = id
						except:
							try:
								id_to_KG_name[id] = RU.get_id_from_property(id_to_name[id].lower(), 'name', label="disease")
								if id_to_KG_name[id] is None:
									assert False
								id_to_id[id_to_KG_name[id]] = id
							except:
								pass

			# get the graph (one call) of all the nodes that wer mapped
			KG_names = []
			for id in ids_sorted_top_n:
				if id_to_KG_name[id] is not None:
					KG_names.append(id_to_KG_name[id])

			if not KG_names:
				error_message = "Sorry, Columbia Open Health Data has no data on the use of %s" % drug_description
				error_code = "EmptyResult"
				response.add_error_message(error_code, error_message)
				response.print()
				return 1

			all_conditions_graph = RU.get_graph_from_nodes(KG_names)

			# Get the info of the mapped nodes
			id_to_info = dict()
			for u, data in all_conditions_graph.nodes(data=True):
				id = data['properties']['id']
				id = id_to_id[id]
				id_to_info[id] = data

			# for each condition, return the results (with the nice sub-graph if the cohd id's were mapped)
			for id in ids_sorted_top_n:
				if id_to_KG_name[id] is not None:
					to_print = "According to the Columbia Open Health Data, when %s is used to treat patients, the condition %s is seen with much %s frequency than expected " \
								"(log ratio = %f)." % (
					drug_description, id_to_name[id], more_less, id_to_frequency[id])
					nodes = []
					disease_node_info = id_to_info[id]
					nodes.append((2, disease_node_info))
					nodes.append((1, drug_node_info))
					edges = [(1, 2, {'id': 3, 'properties': {'is_defined_by': 'RTX',
							'predicate': edge_indication,
							'provided_by': 'COHD',
							'relation': edge_indication,
							'seed_node_uuid': '-1',
							'source_node_uuid': drug_node_info['properties']['UUID'],
							'target_node_uuid': disease_node_info['properties']['UUID']},
							'type': 'treats'})]
					response.add_subgraph(nodes, edges, to_print, id_to_frequency[id])
				else:
					to_print = "According to the Columbia Open Health Data, when %s is used to treat patients, the condition %s is seen with much %s frequency than expected " \
								"(log ratio = %f). This condition could not be mapped to any condition in our " \
							"Knowledge graph, so no graph is shown." % (
						drug_description, id_to_name[id], more_less, id_to_frequency[id])
					g = RU.get_node_as_graph(drug_id)
					response.add_subgraph(g.nodes(data=True), g.edges(data=True), to_print, id_to_frequency[id])
			response.print()

	@staticmethod
	def describe():
		output = "Answers questions of the form: 'What conditions appear less often than expected when taking $drug?'" + "\n"
		# TODO: subsample disease nodes
		return output


def main():
	parser = argparse.ArgumentParser(description="Answers questions of the form: 'What conditions appear less often than expected when taking $drug?'",
									formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-d', '--drug', type=str, help="drug ID/name", default="CHEMBL154")
	parser.add_argument('-r', '--reverse', action='store_true', help="Include if you want the least common diseases, don't include if you want the most common")
	parser.add_argument('-c', '--conservative', action='store_true', help="Include if you want exact matches to drug name (so excluding combo drugs)")
	parser.add_argument('-j', '--json', action='store_true', help='Flag specifying that results should be printed in JSON format (to stdout)', default=False)
	parser.add_argument('--describe', action='store_true', help='Print a description of the question to stdout and quit', default=False)
	parser.add_argument('--num_show', type=int, help='Maximum number of results to return', default=20)

	# Parse and check args
	args = parser.parse_args()
	drug_id = args.drug
	is_rare = args.reverse
	is_conservative = args.conservative
	use_json = args.json
	describe_flag = args.describe
	num_show = args.num_show


	# Initialize the question class
	Q = SurprisingSolution()

	if describe_flag:
		res = Q.describe()
		print(res)
	else:
		Q.answer(drug_id, use_json=use_json, num_show=num_show, rev=is_rare, conservative=is_conservative)
		#Q.answer(drug_id, use_json=True, num_show=num_show, rev=not (is_rare), conservative=is_conservative)

if __name__ == "__main__":
	main()
