import json


class WriteDefaultJson:

    def __init__(self,fp):
        """

        :param fp:
        """
        self.filePath = fp
        self.writeJson()

    def writeJson(self):
        """

        :return:
        """
        data = {
            "comp1": {
                "inputImg1": "figure_1_input/cells_2_1.png",
                "inputImg2":"figure_1_input/cells_2_2.png",
                "algorithms": {
                    "surf":{
                        "min_hess":400,
                        "lowes_ratio":0.5,
                        "min_num_in_cluster_to_accept":1,
                        "cluster_gap":40,
                        "line_width":10,
                        "num_matches":7,
                        "outputPath1":"figure_1_output/cells_2_1_surf.jpg",
                        "outputPath2":"figure_1_output/cells_2_2_surf.jpg",
                        "outputFile": "figure_1_output/cells_2_1&2_surf.json",
                        "b_w": False,
                        "color":[],
                        "flann":{
                            "default":True,
                            "flann_index_kdtree":1,
                            "num_trees":5,
                            "num_checks":50
                        }
                    },
                    "sift":{
                        "lowes_ratio":0.5,
                        "min_num_in_cluster_to_accept":1,
                        "cluster_gap":40,
                        "line_width":10,
                        "num_matches":7,
                        "outputPath1":"figure_1_output/cells_2_1_sift.jpg",
                        "outputPath2":"figure_1_output/cells_2_2_sift.jpg",
                        "outputFile": "figure_1_output/cells_2_1&2_sift.json",
                        "b_w": False,
                        "color":[],
                        "flann":{
                            "default":True,
                            "flann_index_kdtree":1,
                            "num_trees":5,
                            "num_checks":50
                        }
                    },
                    "orb":{
                        "num_features":10000,
                        "lowes_ratio":0.6,
                        "min_num_in_cluster_to_accept":1,
                        "cluster_gap":40,
                        "line_width":10,
                        "num_matches":7,
                        "outputPath1":"figure_1_output/cells_2_1_orb.jpg",
                        "outputPath2":"figure_1_output/cells_2_2_orb.jpg",
                        "outputFile": "figure_1_output/cells_2_1&2_orb.json",
                        "b_w": False,
                        "color":[],
                        "flann":{
                            "default":True,
                            "flann_index_kdtree":1,
                            "num_trees":5,
                            "num_checks":50
                        }
                    },
                    "template":{
                        "step_size":10,
                        "win_size":(100,100),
                        "cor_thresh":0.6,
                        "line_width":10,
                        "min_num_in_cluster_to_accept":1,
                        "cluster_gap":5,
                        "outputPath1":"figure_1_output/cells_2_1_template.jpg",
                        "outputPath2":"figure_1_output/cells_2_2_template.jpg",
                        "outputFile": "figure_1_output/cells_2_1&2_template.json",
                        "b_w": False,
                        "color":[]
                    }
                }
            },
            "comp2": {
                "inputImg1": "figure_1_input/cells_19_1.png",
                "inputImg2":"figure_1_input/cells_19_2.png",
                "algorithms": {
                    "surf":{
                        "min_hess":400,
                        "lowes_ratio":0.5,
                        "min_num_in_cluster_to_accept":1,
                        "cluster_gap":40,
                        "line_width":5,
                        "num_matches":7,
                        "outputPath1":"figure_1_output/cells_19_1_surf.jpg",
                        "outputPath2":"figure_1_output/cells_19_2_surf.jpg",
                        "outputFile": "figure_1_output/cells_19_1&2_surf.json",
                        "b_w": False,
                        "color":[],
                        "flann":{
                            "default":True,
                            "flann_index_kdtree":1,
                            "num_trees":5,
                            "num_checks":50
                        }
                    },
                    "sift":{
                        "lowes_ratio":0.5,
                        "min_num_in_cluster_to_accept":1,
                        "cluster_gap":40,
                        "line_width":5,
                        "num_matches":7,
                        "outputPath1":"figure_1_output/cells_19_1_sift.jpg",
                        "outputPath2":"figure_1_output/cells_19_2_sift.jpg",
                        "outputFile": "figure_1_output/cells_19_1&2_sift.json",
                        "b_w": False,
                        "color":[],
                        "flann":{
                            "default":True,
                            "flann_index_kdtree":1,
                            "num_trees":5,
                            "num_checks":50
                        }
                    },
                    "orb":{
                        "num_features":10000,
                        "lowes_ratio":0.5,
                        "min_num_in_cluster_to_accept":1,
                        "cluster_gap":40,
                        "line_width":5,
                        "num_matches":7,
                        "outputPath1":"figure_1_output/cells_19_1_orb.jpg",
                        "outputPath2":"figure_1_output/cells_19_2_orb.jpg",
                        "outputFile": "figure_1_output/cells_19_1&2_orb.json",
                        "b_w": False,
                        "color":[],
                        "flann":{
                            "default":True,
                            "flann_index_kdtree":1,
                            "num_trees":5,
                            "num_checks":50
                        }
                    },
                    "template":{
                        "step_size":4,
                        "win_size":(30,30),
                        "cor_thresh":0.92,
                        "line_width":5,
                        "min_num_in_cluster_to_accept":1,
                        "cluster_gap":5,
                        "outputPath1":"figure_1_output/cells_19_1_template.jpg",
                        "outputPath2":"figure_1_output/cells_19_2_template.jpg",
                        "outputFile": "figure_1_output/cells_19_1&2_template.json",
                        "b_w": False,
                        "color":[]
                    }
                }
            },
            "comp3": {
                "inputImg1": "figure_1_input/cells_19_3.png",
                "inputImg2":"figure_1_input/cells_19_4.png",
                "algorithms": {
                    "surf":{
                        "min_hess":400,
                        "lowes_ratio":0.6,
                        "min_num_in_cluster_to_accept":1,
                        "cluster_gap":40,
                        "line_width":5,
                        "num_matches":7,
                        "outputPath1":"figure_1_output/cells_19_3_surf.jpg",
                        "outputPath2":"figure_1_output/cells_19_4_surf.jpg",
                        "outputFile": "figure_1_output/cells_19_3&4_surf.json",
                        "b_w": False,
                        "color":[],
                        "flann":{
                            "default":True,
                            "flann_index_kdtree":1,
                            "num_trees":5,
                            "num_checks":50
                        }
                    },
                    "sift":{
                        "lowes_ratio":0.6,
                        "min_num_in_cluster_to_accept":1,
                        "cluster_gap":40,
                        "line_width":5,
                        "num_matches":7,
                        "outputPath1":"figure_1_output/cells_19_3_sift.jpg",
                        "outputPath2":"figure_1_output/cells_19_4_sift.jpg",
                        "outputFile": "figure_1_output/cells_19_3&4_sift.json",
                        "b_w": False,
                        "color":[],
                        "flann":{
                            "default":True,
                            "flann_index_kdtree":1,
                            "num_trees":5,
                            "num_checks":50
                        }
                    },
                    "orb":{
                        "num_features":10000,
                        "lowes_ratio":0.6,
                        "min_num_in_cluster_to_accept":1,
                        "cluster_gap":40,
                        "line_width":5,
                        "num_matches":7,
                        "outputPath1":"figure_1_output/cells_19_3_orb.jpg",
                        "outputPath2":"figure_1_output/cells_19_4_orb.jpg",
                        "outputFile": "figure_1_output/cells_19_3&4_orb.json",
                        "b_w": False,
                        "color":[],
                        "flann":{
                            "default":True,
                            "flann_index_kdtree":1,
                            "num_trees":5,
                            "num_checks":50
                        }
                    },
                    "template":{
                        "step_size":4,
                        "win_size":(50,50),
                        "cor_thresh":0.9,
                        "line_width":5,
                        "min_num_in_cluster_to_accept":1,
                        "cluster_gap":5,
                        "outputPath1":"figure_1_output/cells_19_3_template.jpg",
                        "outputPath2":"figure_1_output/cells_19_4_template.jpg",
                        "outputFile": "figure_1_output/cells_19_3&4_template.json",
                        "b_w": False,
                        "color":[]
                    }
                }
            }
        }

        with open(self.filePath, 'w') as fp:
            json.dump(data, fp)
