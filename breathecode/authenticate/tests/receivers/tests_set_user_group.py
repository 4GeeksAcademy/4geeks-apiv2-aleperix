from ..mixins.new_auth_test_case import AuthTestCase


class ModelProfileAcademyTestSuite(AuthTestCase):
    """
    🔽🔽🔽 Adding a ProfileAcademy
    """
    def test_adding_a_profile_academy(self):
        model = self.bc.database.create(profile_academy=1)

        self.assertEqual(self.bc.database.list_of('auth.Group'), [])
        self.assertEqual(self.bc.format.table(model.profile_academy.user.groups.all()), [])

    """
    🔽🔽🔽 Adding a ProfileAcademy and Group doesn't match
    """

    def test_adding_a_profile_academy__the_group_name_does_not_match(self):
        # keep separated
        model1 = self.bc.database.create(group=1)  # keep before user
        model2 = self.bc.database.create(profile_academy=1)

        self.assertEqual(self.bc.database.list_of('auth.Group'), [self.bc.format.to_dict(model1.group)])
        self.assertEqual(self.bc.format.table(model2.profile_academy.user.groups.all()), [])

    """
    🔽🔽🔽 Adding a ProfileAcademy and Group match but Role slug does't match
    """

    def test_adding_a_profile_academy__the_role_slug_does_not_match(self):
        # keep separated
        group = {'name': 'Student'}
        model1 = self.bc.database.create(group=group)  # keep before user
        model2 = self.bc.database.create(profile_academy=1)

        self.assertEqual(self.bc.database.list_of('auth.Group'), [self.bc.format.to_dict(model1.group)])
        self.assertEqual(self.bc.format.table(model2.profile_academy.user.groups.all()), [])

    """
    🔽🔽🔽 Adding a ProfileAcademy and Group match but Role slug match, status INVITED
    """

    def test_adding_a_profile_academy__the_group_name_and_role_slug_match__status_invited(self):
        # keep separated
        group = {'name': 'Student'}
        model1 = self.bc.database.create(group=group)  # keep before user
        model2 = self.bc.database.create(profile_academy=1, role='student')

        self.assertEqual(self.bc.database.list_of('auth.Group'), [self.bc.format.to_dict(model1.group)])
        self.assertEqual(self.bc.format.table(model2.profile_academy.user.groups.all()), [])

    """
    🔽🔽🔽 Adding a ProfileAcademy and Group match but Role slug match, status ACTIVE
    """

    def test_adding_a_profile_academy__the_group_name_and_role_slug_match__status_active(self):
        # keep separated
        group = {'name': 'Student'}
        profile_academy = {'status': 'ACTIVE'}
        model1 = self.bc.database.create(group=group)  # keep before user
        model2 = self.bc.database.create(profile_academy=profile_academy, role='student')

        self.assertEqual(self.bc.database.list_of('auth.Group'), [self.bc.format.to_dict(model1.group)])
        self.assertEqual(self.bc.format.table(model2.profile_academy.user.groups.all()), [
            self.bc.format.to_dict(model1.group),
        ])


class ModelUserTestSuite(AuthTestCase):
    """
    🔽🔽🔽 Adding a User
    """
    def test_adding_a_user(self):
        model = self.bc.database.create(user=1)

        self.assertEqual(self.bc.database.list_of('auth.Group'), [])
        self.assertEqual(self.bc.format.table(model.user.groups.all()), [])

    """
    🔽🔽🔽 Adding a User and Group doesn't match
    """

    def test_adding_a_user__the_group_name_does_not_match(self):
        # keep separated
        model1 = self.bc.database.create(group=1)  # keep before user
        model2 = self.bc.database.create(user=1)

        self.assertEqual(self.bc.database.list_of('auth.Group'), [self.bc.format.to_dict(model1.group)])
        self.assertEqual(self.bc.format.table(model2.user.groups.all()), [])

    """
    🔽🔽🔽 Adding a User and Group with name Default
    """

    def test_adding_a_user__the_group_name_match(self):
        group = {'name': 'Default'}
        model1 = self.bc.database.create(group=group)  # keep before user
        model2 = self.bc.database.create(user=1)

        self.assertEqual(self.bc.database.list_of('auth.Group'), [self.bc.format.to_dict(model1.group)])
        self.assertEqual(self.bc.format.table(model2.user.groups.all()), [{'id': 1, 'name': 'Default'}])


class ModelMentorProfileTestSuite(AuthTestCase):
    """
    🔽🔽🔽 Adding a ProfileAcademy
    """
    def test_adding_a_mentor_profile(self):
        model = self.bc.database.create(mentor_profile=1)

        self.assertEqual(self.bc.database.list_of('auth.Group'), [])
        self.assertEqual(self.bc.format.table(model.mentor_profile.user.groups.all()), [])

    """
    🔽🔽🔽 Adding a ProfileAcademy and Group doesn't match
    """

    def test_adding_a_mentor_profile__the_group_name_does_not_match(self):
        # keep separated
        model1 = self.bc.database.create(group=1)  # keep before user
        model2 = self.bc.database.create(mentor_profile=1)

        self.assertEqual(self.bc.database.list_of('auth.Group'), [self.bc.format.to_dict(model1.group)])
        self.assertEqual(self.bc.format.table(model2.mentor_profile.user.groups.all()), [])

    """
    🔽🔽🔽 Adding a ProfileAcademy and Group match
    """

    def test_adding_a_mentor_profile__the_group_name_match(self):
        # keep separated
        group = {'name': 'Mentor'}
        model1 = self.bc.database.create(group=group)  # keep before user
        model2 = self.bc.database.create(mentor_profile=1)

        self.assertEqual(self.bc.database.list_of('auth.Group'), [self.bc.format.to_dict(model1.group)])
        self.assertEqual(self.bc.format.table(model2.mentor_profile.user.groups.all()), [
            self.bc.format.to_dict(model1.group),
        ])
