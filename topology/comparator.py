class SkeletonComparator:
    """
    Compara dos SkeletonFeatures.
    """

    def compare(self, features_a, features_b):
        """
        Calcula la similitud total entre dos esqueletos.
        """

        score = 0.0

        score += self.compare_topology(features_a, features_b)

        score += self.compare_geometry(features_a, features_b)

        score += self.compare_branches(features_a, features_b)

        score += self.compare_bbox(features_a, features_b)

        return score / 4.0

    ################################################
    # TOPOLOGY
    ################################################

    def compare_topology(self, features_a, features_b):

        score = 0.0

        if features_a.node_count == features_b.node_count:
            score += 1.0

        if features_a.edge_count == features_b.edge_count:
            score += 1.0

        if features_a.root_count == features_b.root_count:
            score += 1.0

        if features_a.leaf_count == features_b.leaf_count:
            score += 1.0

        if features_a.branch_count == features_b.branch_count:
            score += 1.0

        if features_a.max_children == features_b.max_children:
            score += 1.0

        if features_a.max_depth == features_b.max_depth:
            score += 1.0

        return score / 7.0
        

    ################################################
    # GEOMETRY
    ################################################

    def compare_geometry(self, features_a, features_b):
        """
        Compara las características geométricas.
        """

        score = 0.0

        score += self._compare_float(
            features_a.bone_length_min,
            features_b.bone_length_min,
        )

        score += self._compare_float(
            features_a.bone_length_max,
            features_b.bone_length_max,
        )

        score += self._compare_float(
            features_a.bone_length_mean,
            features_b.bone_length_mean,
        )

        return score / 3.0

    ################################################
    # BRANCHES
    ################################################

    def compare_branches(self, features_a, features_b):
        """
        Compara las características de las ramas.
        """

        score = 0.0

        score += self._compare_float(
            features_a.branch_length_min,
            features_b.branch_length_min,
        )

        score += self._compare_float(
            features_a.branch_length_max,
            features_b.branch_length_max,
        )

        score += self._compare_float(
            features_a.branch_length_mean,
            features_b.branch_length_mean,
        )
        
        return score / 3.0

    ################################################
    # BBOX
    ################################################

    def compare_bbox(self, features_a, features_b):
        """
        Compara las dimensiones de la Bounding Box.
        """

        score = 0.0

        ################################################
        # DIMENSIONES
        ################################################

        for a, b in zip(
            features_a.bbox_extents,
            features_b.bbox_extents,
        ):
            score += self._compare_float(a, b)

        ################################################
        # PROPORCIONES
        ################################################

        score += self._compare_float(
            features_a.bbox_width_ratio,
            features_b.bbox_width_ratio,
        )

        score += self._compare_float(
            features_a.bbox_height_ratio,
            features_b.bbox_height_ratio,
        )

        return score / 5
    ################################################
    # UTILIDADES
    ################################################
    
    def _compare_float(self, value_a, value_b):
        """
        Compara dos valores numéricos y devuelve una similitud
        entre 0.0 y 1.0.
        """

        if value_a == value_b:
            return 1.0

        maximum = max(abs(value_a), abs(value_b))

        if maximum == 0:
            return 1.0

        difference = abs(value_a - value_b)

        score = 1.0 - (difference / maximum)

        return max(0.0, score)