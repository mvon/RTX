# A collection of scripts to interact with Columbia open health data

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
	from QueryCOHD import QueryCOHD

import CustomExceptions


class COHDUtilities:
	def __init__(self):
		None

	@staticmethod
	def get_conditions_treating(drug_description, conservative=False):
		"""
		Get all the conditions that are associated with a drug.
		:param drug_description: string (eg. 'Naproxen')
		:param conservative: bool (True= use exact matching for mapping drug to COHD, False = use all synonyms returned by COHD)
		:return: dictionary of dictionaries (eg. keys are concept IDs, values look like:
		{'associated_concept_id': 134736,
  		'associated_concept_name': 'Backache',
		'concept_count': 112,
		'concept_frequency': 2.101665438505926e-05,
		'concept_id': 1115008}
		"""

		# Get the concept ID of the drug
		drug_concepts = QueryCOHD.find_concept_ids(drug_description)
		drug_ids = []
		if conservative:
			for concept in drug_concepts:
				if concept['concept_name'].lower() == drug_description.lower():
					drug_ids.append(concept['concept_id'])
		if not conservative:
			for concept in drug_concepts:
				drug_ids.append(concept['concept_id'])

		# get all the associated conditions
		associated_concepts = []
		for drug_id in drug_ids:
			associated_concepts += QueryCOHD.get_associated_concept_domain_freq(drug_id, "Condition")

		# go through and sum them all up (no need for conservative flag since that will only be a single one)
		# get all the unique condition ids
		associated_concept_ids = set()
		for concept in associated_concepts:
			associated_concept_ids.add(concept['associated_concept_id'])

		# go through the associated conditions, summing up the concept counts
		result_dict = dict()
		for associated_concept in associated_concepts:
			id = associated_concept['associated_concept_id']
			if id in result_dict:
				result_dict[id]['concept_count'] += associated_concept['concept_count']
			else:
				result_dict[id] = associated_concept

		# We'll need to adjust the frequencies in terms of the total patients treated with this drug
		total_associated_condition_counts = 0
		for id in result_dict:
			total_associated_condition_counts += result_dict[id]['concept_count']

		for id in result_dict:
			result_dict[id]['concept_frequency'] = result_dict[id]['concept_count'] / float(total_associated_condition_counts)

		return result_dict

	@staticmethod
	def get_surprising_conditions_treating(drug_description, conservative=False):
		"""
		Get all the suprising conditions that are associated with a drug.
		:param drug_description: string (eg. 'Naproxen')
		:param conservative: bool (True= use exact matching for mapping drug to COHD, False = use all synonyms returned by COHD)
		:return: dictionary of dictionaries (eg. keys are concept IDs, values look like:
		{'concept_id_2': 134736,
		  'concept_2_name': 'Backache',
		'concept_2_domain': 'Condition',
		'observed_count': 200,
		'expected_count': 100,
		'ln_ratio': 0.69314718056,
		'dataset_id': 3,
		'concept_id_1': 1115008}
		"""

		# Get the concept ID of the drug
		drug_concepts = QueryCOHD.find_concept_ids(drug_description, dataset_id=3)
		drug_ids = []
		if conservative:
			for concept in drug_concepts:
				if concept['concept_name'].lower() == drug_description.lower():
					drug_ids.append(concept['concept_id'])
		if not conservative:
			for concept in drug_concepts:
				drug_ids.append(concept['concept_id'])

		# get all the associated conditions
		associated_concepts = []
		for drug_id in drug_ids:
			associated_concepts += QueryCOHD.get_obs_exp_ratio(str(drug_id), domain="Condition", dataset_id=3)


		# go through and sum them all up (no need for conservative flag since that will only be a single one)
		# get all the unique condition ids
		associated_concept_ids = set()
		for concept in associated_concepts:
			associated_concept_ids.add(concept['concept_id_2'])

		# go through the associated conditions, summing up the observed counts and expected counts
		result_dict = dict()
		for associated_concept in associated_concepts:
			id = associated_concept['concept_id_2']
			if id in result_dict:
				result_dict[id]['observed_count'] += associated_concept['observed_count']
				result_dict[id]['expected_count'] += associated_concept['expected_count']
			else:
				result_dict[id] = associated_concept

		# We'll need to adjust the ln_ratio to account for multiple mappings
		for id in result_dict:
			result_dict[id]['ln_ratio'] = math.log(result_dict[id]['observed_count'] / result_dict[id]['expected_count'])

		return result_dict

if __name__ == "__main__":
	q = COHDUtilities()
	print(q.get_conditions_treating('Naproxen', conservative=True))
	print("\n")
	print(q.get_conditions_treating('Naproxen', conservative=False))



