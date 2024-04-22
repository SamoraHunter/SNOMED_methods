import os
import re
import sys
from typing import List, Tuple

import numpy as np
import pandas as pd
import requests
from tqdm import tqdm


class snomed_relations:

    def __init__(
        self,
        medcat=False,
        snowstorm=False,
        aliencat=False,
        dgx=False,
        dhcap=False,
        dhcap02=True,
        snomed_rf2_full_path=None,
        medcat_path=None,
    ):

        sys.path.insert(0, "..")

        if snomed_rf2_full_path is None:

            current_dir = os.getcwd()

            os.path.abspath(
                os.path.join(
                    current_dir,
                    "..",
                    "snomed",
                    "SnomedCT_InternationalRF2_PRODUCTION_20231101T120000Z",
                    "SnomedCT_InternationalRF2_PRODUCTION_20231101T120000Z",
                    "Full",
                    "Terminology",
                    "sct2_StatedRelationship_Full_INT_20231101.txt",
                )
            )

            self.df = pd.read_csv(
                "/home/cogstack/samora/_data/snomed/SnomedCT_InternationalRF2_PRODUCTION_20231101T120000Z/Full/Terminology/sct2_StatedRelationship_Full_INT_20231101.txt",
                sep="\t",
                header=0,
            )
        else:
            try:
                self.df = pd.read_csv(snomed_rf2_full_path, sep="\t", header=0)
            except Exception as e:
                print(
                    "failed to read snomed file, looking for file like sct2_StatedRelationship_Full_INT_20231101.txt"
                )

        self.medcat = medcat

        self.snowstorm = snowstorm

        if self.medcat:

            from medcat.cat import CAT

            if medcat_path == None:

                if aliencat:
                    self.cat = CAT.load_model_pack(
                        "/home/aliencat/samora/HFE/HFE/medcat_models/medcat_model_pack_316666b47dfaac07.zip"
                    )

                elif dgx:
                    self.cat = CAT.load_model_pack(
                        "/data/AS/Samora/HFE/HFE/v18/"
                        + "medcat_models/20230328_trained_model_hfe_redone/medcat_model_pack_316666b47dfaac07"
                    )

                elif dhcap:
                    self.cat = CAT.load_model_pack(
                        "/home/jovyan/work/"
                        + "medcat_models/medcat_model_pack_316666b47dfaac07.zip"
                    )

                elif dhcap02:
                    self.cat = CAT.load_model_pack(
                        "/home/cogstack/samora/"
                        + "/_data/"
                        + "medcat_models/medcat_model_pack_316666b47dfaac07.zip"
                    )

            else:
                self.cat = CAT.load_model_pack(medcat_path)

    def get_children(self, cui):
        try:
            cui = int(cui)
            children = self.df[self.df["destinationId"] == cui]["sourceId"].to_list()
            return children
        except ValueError:
            print("Error: 'cui' must be convertible to an integer.")
            return []

    def get_parents(self, cui):
        try:
            cui = int(cui)
            parents = self.df[self.df["sourceId"] == cui]["sourceId"].to_list()
            return parents
        except ValueError:
            print("Error: 'cui' must be convertible to an integer.")
            return []

    def expand_codes(self, filter_root_cui, debug=False):

        if self.snowstorm:
            self.expand_codes_snowstorm(filter_root_cui, debug=False)

        else:
            self.expand_codes_local(filter_root_cui)

    # def expand_codes_local(self, filter_root_cui, debug = False):

    #     if debug:

    #         print("Entering expand_codes_local function")
    #         print(f"filter_root_cui: {filter_root_cui}")

    #     retrieved_codes_temp = []
    #     retrieved_names_temp = []

    #     cr = self.expand_codes_parents_local(filter_root_cui, debug=debug)

    #     if debug:
    #         print(f"cr: {len(cr)}")

    #     ar = self.expand_codes_children_local(filter_root_cui, debug=debug)

    #     if debug:
    #         print(f"ar: {len(ar)}")

    #     retrieved_codes_temp.extend(cr)
    #     retrieved_codes_temp.extend(ar)
    #     retrieved_names_temp.extend(self.get_pretty_name_list(cr))
    #     retrieved_names_temp.extend(self.get_pretty_name_list(ar))
    #     retrieved_codes_temp = list(set(retrieved_codes_temp))
    #     retrieved_names_temp = list(set(retrieved_names_temp))

    #     if debug:
    #         print(f"{len(retrieved_codes_temp)} retrieved_codes: {retrieved_codes_temp}")

    #     return retrieved_codes_temp, retrieved_names_temp

    def expand_codes_local(self, filter_root_cui, debug=False):

        if debug:

            print("Entering expand_codes_local function")
            print(f"filter_root_cui: {filter_root_cui}")

        retrieved_codes_temp = []
        retrieved_names_temp = []

        cr = self.expand_codes_parents_local(filter_root_cui, debug=debug)

        if debug:
            print(f"cr: {len(cr)}")

        ar = self.expand_codes_children_local(filter_root_cui, debug=debug)

        if debug:
            print(f"ar: {len(ar)}")

        retrieved_codes_temp.extend(cr[0])
        retrieved_codes_temp.extend(ar[0])
        retrieved_names_temp.extend(cr[1])
        retrieved_names_temp.extend(ar[1])
        retrieved_codes_temp = list(set(retrieved_codes_temp))
        retrieved_names_temp = list(set(retrieved_names_temp))

        if debug:
            print(
                f"{len(retrieved_codes_temp)} retrieved_codes: {retrieved_codes_temp}"
            )

        return retrieved_codes_temp, retrieved_names_temp

    def get_pretty_name(self, cui):

        assert self.medcat
        return self.cat.cdb.cui2preferred_name.get(str(cui))

    def get_pretty_name_list(self, cui_list):

        pretty_name_list = []

        for i in range(0, len(cui_list)):
            pretty_name_list.append(self.get_pretty_name(cui_list[i]))
        return pretty_name_list

    def expand_codes_children_local(self, filter_root_cui, debug=False):

        if debug:

            print("expand_codes_children_local function")
            print(f"filter_root_cui: {filter_root_cui}")

        retrieved_names_temp = []

        children_codes = self.get_children(filter_root_cui)

        assert self.medcat

        # for i in range(0, len(children_codes)):
        #     retrieved_names_temp.append(self.cat.cdb.cui2preferred_name.get(children_codes[i]))

        retrieved_names_temp = self.get_pretty_name_list(children_codes)

        return children_codes, retrieved_names_temp

    def expand_codes_parents_local(self, filter_root_cui, debug=False):

        if debug:

            print("expand_codes_parents_local function")
            print(f"filter_root_cui: {filter_root_cui}")

        retrieved_names_temp = []

        parent_codes = self.get_parents(filter_root_cui)

        assert self.medcat

        # for i in range(0, len(parent_codes)):
        #     retrieved_names_temp.append(self.cat.cdb.cui2preferred_name.get(parent_codes[i]))

        retrieved_names_temp = self.get_pretty_name_list(parent_codes)

        return parent_codes, retrieved_names_temp

    def expand_codes_snowstorm(self, filter_root_cui, debug=False):
        # debug = True
        if debug:

            print("Entering expand_codes function")
            print(f"filter_root_cui: {filter_root_cui}")

        retrieved_codes_temp = []
        retrieved_names_temp = []

        c = self.get_snowstorm_response_children(filter_root_cui)
        if debug:
            print(f"c: {len(c)}")

        a = self.get_snowstorm_response_ancestors(filter_root_cui)
        if debug:
            print(f"a: {len(a)}")

        cr = self.parse_snowstorm_response_to_cui_name(c)
        if debug:
            print(f"cr: {len(cr[0])}")

        ar = self.parse_snowstorm_response_to_cui_name(a)
        if debug:
            print(f"ar: {len(ar[0])}")

        retrieved_codes_temp.extend(cr[0])
        retrieved_codes_temp.extend(ar[0])
        retrieved_names_temp.extend(cr[1])
        retrieved_names_temp.extend(ar[1])
        retrieved_codes_temp = list(set(retrieved_codes_temp))
        retrieved_names_temp = list(set(retrieved_names_temp))

        if debug:
            print(
                f"{len(retrieved_codes_temp)} retrieved_codes: {retrieved_codes_temp}"
            )

        return retrieved_codes_temp, retrieved_names_temp

    def recursive_code_expansion(self, filter_root_cui, n_recursion=3, debug=False):
        retrieved_codes = [filter_root_cui]
        retrieved_names = []

        print(f"Retrieving {filter_root_cui} with recursion {n_recursion}")

        for i in tqdm(range(n_recursion)):

            if debug:
                print(i, len(retrieved_codes))
                print(retrieved_names[0:5], f"...{len(retrieved_names)}")

            retrieved_codes = list(set(retrieved_codes))

            for j in range(0, len(retrieved_codes)):
                current_filter_root_cui = retrieved_codes[j]

                raw = self.expand_codes_local(
                    filter_root_cui=current_filter_root_cui, debug=debug
                )

                codes = raw[0]
                names = raw[1]

                retrieved_codes.extend(codes)
                retrieved_names.extend(names)

                retrieved_codes = list(set(retrieved_codes))
                retrieved_names = list(set(retrieved_names))

        if debug:

            print(f"Final len retrieved_codes {len(retrieved_codes)}")

        return retrieved_codes, retrieved_names

    def get_medcat_cdb_most_similar(
        self, cui, context_type="xxxlong", type_id_filter=[], topn=10
    ):

        try:
            res = self.cat.cdb.most_similar(
                cui, context_type=context_type, type_id_filter=type_id_filter, topn=topn
            )
        except Exception as e:
            print(e)
            return [], []

        names = []
        codes = []

        key_list = list(res.keys())

        for elem in key_list:

            codes.append(elem)

        names = self.get_pretty_name_list(codes)

        return codes, names

    def build_lists_medcat_snomedtree(self, input_list, medcat=False, snomed=True):
        retrieved_codes = []
        retrieved_names = []

        if snomed:
            for item in input_list:
                codes, names = self.recursive_code_expansion(item)
                retrieved_codes.extend(codes)
                retrieved_names.extend(names)

        if medcat:
            for item in input_list:
                codes, names = self.get_medcat_cdb_most_similar(item)
                retrieved_codes.extend(codes)
                retrieved_names.extend(names)

        retrieved_codes = [int(code) for code in retrieved_codes]

        return retrieved_codes, retrieved_names

        # type-id t-16 etc
        # {T-38}    198890
        # {T-40}    173894
        # {T-11}     77284
        # {T-39}     64291
        # {T-18}     44201
        # {T-35}     34778
        # {T-6}      32944
        # {T-55}     27626
        # {T-33}     15117
        # {T-42}     14591

    def get_medcat_similar_score(self, input_cui, target_cui_list, debug=False):
        if debug:
            print(f"Debug: Getting similar scores for input CUI {input_cui}")

        target_cui_list = list(map(str, target_cui_list))

        input_cui = str(input_cui)

        try:
            res = self.cat.cdb.most_similar(
                input_cui, context_type="xxxlong", type_id_filter=[], topn=999999
            )
        except Exception as e:
            print(e)
            return []

        results_list = []

        if debug:
            print(
                f"Debug: Checking similarity score for target CUI list.. {target_cui_list[0:3]}..."
            )

        for i in range(len(target_cui_list)):
            target_cui = target_cui_list[i]

            sim_res = res.get(target_cui)

            if sim_res is not None:

                sim_score = sim_res.get("sim")

            else:

                sim_score = None

            if sim_score is not None:

                results_list.append(sim_score)
            else:
                results_list.append(np.nan)

        if debug:
            print(f"Debug: Result list: {results_list[0:3]}...")

        return results_list

    def append_concept_sim_to_df(self, df, target_concept_sim_list, target_cui_list):

        for elem in target_concept_sim_list:

            df[f"{elem}_concept_sim"] = self.get_medcat_similar_score(
                elem, target_cui_list, debug=True
            )

        return df

    def retrieve_search_synonyms(
        self,
        filter_root_cui,
        n_recursion=10,
        context_type="xxxlong",
        type_id_filter=[],
        topn=50,
        debug=False,
        use_snomed=True,
        use_medcat=True,
    ):
        # Initialize a list to store names
        all_names = []

        # Retrieve data for snomed_tree if use_snomed is True
        retrieved_codes_snomed_tree, retrieved_names_snomed_tree = (
            ([], [])
            if not use_snomed
            else self.recursive_code_expansion(
                filter_root_cui, n_recursion=n_recursion, debug=debug
            )
        )

        # Add names to the list, stripping anything in parentheses
        all_names.extend(
            [
                re.sub(r"\([^)]*\)", "", name).strip()
                for name in retrieved_names_snomed_tree
                if name is not None
            ]
        )

        # Retrieve data for medcat_cdb if use_medcat is True
        retrieved_codes_medcat_cdb, retrieved_names_medcat_cdb = (
            ([], [])
            if not use_medcat
            else self.get_medcat_cdb_most_similar(
                filter_root_cui,
                context_type=context_type,
                type_id_filter=type_id_filter,
                topn=topn,
            )
        )

        # Add names to the list, stripping anything in parentheses
        all_names.extend(
            [
                re.sub(r"\([^)]*\)", "", name).strip()
                for name in retrieved_names_medcat_cdb
                if name is not None
            ]
        )

        return (
            retrieved_codes_snomed_tree,
            retrieved_names_snomed_tree,
            retrieved_codes_medcat_cdb,
            retrieved_names_medcat_cdb,
            all_names,
        )

    def retrieve_search_synonyms_multi(
        self,
        filter_root_cui_list: List[str],
        n_recursion: int = 10,
        context_type: str = "xxxlong",
        type_id_filter: List[int] = [],
        topn: int = 50,
        debug: bool = False,
        use_snomed: bool = True,
        use_medcat: bool = True,
    ) -> Tuple[
        List[List[str]],
        List[List[str]],
        List[List[str]],
        List[List[str]],
        List[str],
        List[str],
    ]:
        """
        Retrieves search synonyms for multiple filter_root_cui values.

        Args:
            filter_root_cui_list (List[str]): List of filter_root_cui values to retrieve search synonyms for.
            n_recursion (int, optional): Number of recursion levels for code expansion. Defaults to 10.
            context_type (str, optional): Type of context. Defaults to 'xxxlong'.
            type_id_filter (List[int], optional): List of type IDs for filtering. Defaults to [].
            topn (int, optional): Top N results to retrieve. Defaults to 50.
            debug (bool, optional): Enable debugging. Defaults to False.
            use_snomed (bool, optional): Use SNOMED for retrieval. Defaults to True.
            use_medcat (bool, optional): Use MedCAT for retrieval. Defaults to True.

        Returns:
            Tuple[List[List[str]], List[List[str]], List[List[str]], List[List[str]], List[str], List[str]]: A tuple containing:
                - List of retrieved codes from SNOMED for each filter_root_cui.
                - List of retrieved names from SNOMED for each filter_root_cui.
                - List of retrieved codes from MedCAT for each filter_root_cui.
                - List of retrieved names from MedCAT for each filter_root_cui.
                - Flat list of all retrieved names.
                - Flat list of all retrieved codes.
        """
        # Initialize lists to store results
        all_retrieved_codes_snomed_tree = []
        all_retrieved_names_snomed_tree = []
        all_retrieved_codes_medcat_cdb = []
        all_retrieved_names_medcat_cdb = []
        all_names = []
        all_codes = []  # New list to store all codes

        # Iterate over each filter_root_cui in the list
        for filter_root_cui in filter_root_cui_list:
            # Retrieve data for snomed_tree if use_snomed is True
            retrieved_codes_snomed_tree, retrieved_names_snomed_tree = (
                ([], [])
                if not use_snomed
                else self.recursive_code_expansion(
                    filter_root_cui, n_recursion=n_recursion, debug=debug
                )
            )

            # Add retrieved data to the lists
            all_retrieved_codes_snomed_tree.append(retrieved_codes_snomed_tree)
            all_retrieved_names_snomed_tree.append(retrieved_names_snomed_tree)

            # Add names to the all_names list, stripping anything in parentheses
            all_names.extend(
                [
                    re.sub(r"\([^)]*\)", "", name).strip()
                    for name in retrieved_names_snomed_tree
                    if name is not None
                ]
            )

            # Add codes to the all_codes list
            all_codes.extend(retrieved_codes_snomed_tree)

            # Retrieve data for medcat_cdb if use_medcat is True
            retrieved_codes_medcat_cdb, retrieved_names_medcat_cdb = (
                ([], [])
                if not use_medcat
                else self.get_medcat_cdb_most_similar(
                    filter_root_cui,
                    context_type=context_type,
                    type_id_filter=type_id_filter,
                    topn=topn,
                )
            )

            # Add retrieved data to the lists
            all_retrieved_codes_medcat_cdb.append(retrieved_codes_medcat_cdb)
            all_retrieved_names_medcat_cdb.append(retrieved_names_medcat_cdb)

            # Add names to the all_names list, stripping anything in parentheses
            all_names.extend(
                [
                    re.sub(r"\([^)]*\)", "", name).strip()
                    for name in retrieved_names_medcat_cdb
                    if name is not None
                ]
            )

            # Add codes to the all_codes list
            all_codes.extend(retrieved_codes_medcat_cdb)

            all_codes = [str(code) for code in all_codes]

        return (
            all_retrieved_codes_snomed_tree,
            all_retrieved_names_snomed_tree,
            all_retrieved_codes_medcat_cdb,
            all_retrieved_names_medcat_cdb,
            all_names,
            all_codes,
        )

    def get_snowstorm_response_children(cui):
        url = f"https://snowstorm.ihtsdotools.org/snowstorm/snomed-ct/browser/MAIN%2FSNOMEDCT-GB/concepts/{cui}/children?form=inferred&includeDescendantCount=false"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            # Add other headers if required
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
