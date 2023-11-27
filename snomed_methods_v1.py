
import os, sys
import pandas as pd
import numpy as np
from tqdm import tqdm

class snomed_relations:
    
    def __init__(self, medcat = False, snowstorm=False, aliencat = False, dgx = False, dhcap=False, dhcap02 = True):
        
        
        sys.path.insert(0,'/home/aliencat/samora/gloabl_files')
        sys.path.insert(0,'/data/AS/Samora/gloabl_files')
        sys.path.insert(0,'/home/jovyan/work/gloabl_files')
        sys.path.insert(0, '/home/cogstack/samora/_data/gloabl_files')
        
        self.df = pd.read_csv('/home/cogstack/samora/_data/snomed/SnomedCT_InternationalRF2_PRODUCTION_20231101T120000Z/Full/Terminology/sct2_StatedRelationship_Full_INT_20231101.txt', sep='\t', header=0)
        
        self.medcat = medcat
        
        self.snowstorm = snowstorm
        
        
        if(self.medcat):
            
            from medcat.cat import CAT
            
            if(aliencat):
                self.cat = CAT.load_model_pack('/home/aliencat/samora/HFE/HFE/medcat_models/medcat_model_pack_316666b47dfaac07.zip')
                
            elif(dgx):
                self.cat = CAT.load_model_pack('/data/AS/Samora/HFE/HFE/v18/' + 'medcat_models/20230328_trained_model_hfe_redone/medcat_model_pack_316666b47dfaac07');
                
            elif(dhcap):
                self.cat = CAT.load_model_pack('/home/jovyan/work/' + 'medcat_models/medcat_model_pack_316666b47dfaac07.zip');
                
            elif(dhcap02):
                self.cat = CAT.load_model_pack('/home/cogstack/samora/' + '/_data/' + 'medcat_models/medcat_model_pack_316666b47dfaac07.zip');
        
        
    def get_children(self, cui):
        try:
            cui = int(cui)
            children = self.df[self.df['destinationId'] == cui]['sourceId'].to_list()
            return children
        except ValueError:
            print("Error: 'cui' must be convertible to an integer.")
            return []

    def get_parents(self, cui):
        try:
            cui = int(cui)
            parents = self.df[self.df['sourceId'] == cui]['sourceId'].to_list()
            return parents
        except ValueError:
            print("Error: 'cui' must be convertible to an integer.")
            return []
    
    
    def expand_codes(self, filter_root_cui, debug = False):
        
        if(self.snowstorm):
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
    
    def expand_codes_local(self, filter_root_cui, debug = False):
        
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
            print(f"{len(retrieved_codes_temp)} retrieved_codes: {retrieved_codes_temp}")

        return retrieved_codes_temp, retrieved_names_temp
    
    
    
    def get_pretty_name(self, cui):
        
        assert self.medcat
        return self.cat.cdb.cui2preferred_name.get(str(cui))
            
    
    def get_pretty_name_list(self, cui_list):
        
        pretty_name_list = []
        
        for i in range(0, len(cui_list)):
            pretty_name_list.append(self.get_pretty_name(cui_list[i]))
        return pretty_name_list
        
        
    
    def expand_codes_children_local(self, filter_root_cui, debug = False):
    
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
        
    
    
    def expand_codes_parents_local(self, filter_root_cui, debug = False):
    
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
        #debug = True
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
            print(f"{len(retrieved_codes_temp)} retrieved_codes: {retrieved_codes_temp}")

        return retrieved_codes_temp, retrieved_names_temp
    

    
    def recursive_code_expansion(self, filter_root_cui, n_recursion = 3, debug=False):
        retrieved_codes = [filter_root_cui]
        retrieved_names = []

        print(f"Retrieving {filter_root_cui} with recursion {n_recursion}")

        for i in tqdm(range(n_recursion)): 
            
            if(debug):
                print(i, len(retrieved_codes))
                print(retrieved_names[0:5], f"...{len(retrieved_names)}")
                
            retrieved_codes = list(set(retrieved_codes))

            for j in range(0, len(retrieved_codes)):
                current_filter_root_cui = retrieved_codes[j]

                raw = self.expand_codes_local(filter_root_cui=current_filter_root_cui, debug=debug)

                codes = raw[0]
                names = raw[1]

                retrieved_codes.extend(codes)
                retrieved_names.extend(names)

                retrieved_codes = list(set(retrieved_codes))
                retrieved_names = list(set(retrieved_names))
                
        if(debug):
            
            print(f"Final len retrieved_codes {len(retrieved_codes)}")

        return retrieved_codes, retrieved_names
    
    
    
    def get_medcat_cdb_most_similar(self, cui, context_type = 'xxxlong', type_id_filter=[], topn=10):
        
        try:
            res = self.cat.cdb.most_similar(cui, context_type = context_type, type_id_filter=type_id_filter, topn=topn)
        except Exception as e:
            print(e)
            return [],[]
        
        
        names = []
        codes = []
        
        key_list = list(res.keys())
        
        for elem in key_list:
            
            codes.append(elem)
            
        names = self.get_pretty_name_list(codes)
        
        return codes, names
            
        
        #type-id t-16 etc
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
            res = self.cat.cdb.most_similar(input_cui, context_type='xxxlong', type_id_filter=[], topn=999999)
        except Exception as e:
            print(e)
            return []

        results_list = []
        
        if debug:
                print(f"Debug: Checking similarity score for target CUI list.. {target_cui_list[0:3]}...")

        for i in range(len(target_cui_list)):
            target_cui = target_cui_list[i]

            

            sim_res = res.get(target_cui)
            
            if(sim_res is not None):
                
                sim_score = sim_res.get('sim')
            
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
        
            df[f'{elem}_concept_sim'] = self.get_medcat_similar_score(elem, target_cui_list, debug=True)
        
        return df