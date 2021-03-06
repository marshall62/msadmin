# Generated by Django 2.0.7 on 2018-10-31 16:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Administrator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userName', models.CharField(max_length=45)),
                ('password', models.CharField(max_length=64)),
                ('pw2', models.CharField(max_length=45)),
                ('email', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'administrator',
            },
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('teacher', models.CharField(max_length=50)),
                ('teacherId', models.IntegerField()),
            ],
            options={
                'db_table': 'class',
            },
        ),
        migrations.CreateModel(
            name='ClassConfig',
            fields=[
                ('mouseSaveInterval', models.IntegerField(db_column='mouseSaveInterval')),
                ('postTestOn', models.BooleanField(db_column='showPostSurvey')),
                ('classId', models.IntegerField(db_column='classId', primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'classconfig',
            },
        ),
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categoryCode', models.CharField(max_length=10)),
                ('clusterABCD', models.CharField(max_length=2)),
            ],
            options={
                'db_table': 'cluster',
            },
        ),
        migrations.CreateModel(
            name='FormatTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=100)),
                ('problemFormat', models.TextField()),
                ('enabled', models.BooleanField()),
            ],
            options={
                'db_table': 'quickauthformattemplates',
            },
        ),
        migrations.CreateModel(
            name='Hint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('statementHTML', models.TextField()),
                ('audioResource', models.CharField(max_length=100)),
                ('imageURL', models.CharField(max_length=200)),
                ('hoverText', models.CharField(max_length=200)),
                ('order', models.IntegerField()),
                ('givesAnswer', models.BooleanField()),
                ('placement', models.IntegerField()),
            ],
            options={
                'db_table': 'hint',
            },
        ),
        migrations.CreateModel(
            name='InterventionSelector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('onEvent', models.CharField(max_length=45)),
                ('className', models.CharField(max_length=100)),
                ('config', models.TextField(blank=True)),
                ('description', models.CharField(blank=True, max_length=800)),
                ('briefDescription', models.CharField(blank=True, max_length=120)),
                ('type', models.CharField(choices=[('login', 'login'), ('lesson', 'lesson'), ('tutor', 'tutor')], max_length=10)),
                ('genericParent', models.ForeignKey(blank=True, db_column='generic_is_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='msadmin.InterventionSelector')),
            ],
            options={
                'db_table': 'intervention_selector',
            },
        ),
        migrations.CreateModel(
            name='InterventionSelectorParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('value', models.CharField(max_length=1000)),
                ('isActive', models.BooleanField()),
                ('possibleValues', models.TextField(db_column='possible_values')),
                ('description', models.CharField(max_length=500)),
            ],
            options={
                'db_table': 'is_param_sc',
            },
        ),
        migrations.CreateModel(
            name='ISParamBase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('value', models.CharField(max_length=1000)),
                ('description', models.CharField(max_length=500)),
                ('interventionSelector', models.ForeignKey(db_column='intervention_selector_id', on_delete=django.db.models.deletion.PROTECT, to='msadmin.InterventionSelector')),
            ],
            options={
                'db_table': 'is_param_base',
            },
        ),
        migrations.CreateModel(
            name='ISParamValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=500)),
                ('isParam', models.ForeignKey(db_column='isparamid', on_delete=django.db.models.deletion.PROTECT, to='msadmin.ISParamBase', verbose_name='Base IS Param')),
            ],
            options={
                'db_table': 'is_param_value',
            },
        ),
        migrations.CreateModel(
            name='LC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('className', models.CharField(choices=[('edu.umass.ckc.wo.tutor.agent.JaneNoEmpathicLC', 'JaneNoEmpathicLC'), ('edu.umass.ckc.wo.tutor.agent.JaneSemiEmpathicLC', 'JaneSemiEmpathicLC'), ('edu.umass.ckc.wo.tutor.agent.JaneEmpathicLC', 'JaneEmpathicLC'), ('edu.umass.ckc.wo.tutor.agent.JakeNoEmpathicLC', 'JakeNoEmpathicLC'), ('edu.umass.ckc.wo.tutor.agent.JakeSemiEmpathicLC', 'JakeSemiEmpathicLC'), ('edu.umass.ckc.wo.tutor.agent.JakeEmpathicLC', 'JakeEmpathicLC'), ('edu.umass.ckc.wo.tutor.agent.RuleDrivenLearningCompanion', 'RuleDrivenLearningCompanion')], max_length=200)),
                ('charName', models.CharField(max_length=45)),
                ('description', models.TextField()),
            ],
            options={
                'db_table': 'lc',
            },
        ),
        migrations.CreateModel(
            name='LC2Ruleset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lc', models.ForeignKey(db_column='lcid', on_delete=django.db.models.deletion.PROTECT, to='msadmin.LC')),
            ],
            options={
                'db_table': 'lc_ruleset_map',
            },
        ),
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
            ],
            options={
                'db_table': 'machine',
            },
        ),
        migrations.CreateModel(
            name='Machine2Owner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine', models.ForeignKey(db_column='machineId', on_delete=django.db.models.deletion.PROTECT, to='msadmin.Machine')),
            ],
            options={
                'db_table': 'machine2owner',
            },
        ),
        migrations.CreateModel(
            name='Machine2Part',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine', models.ForeignKey(db_column='machineId', on_delete=django.db.models.deletion.PROTECT, to='msadmin.Machine')),
            ],
            options={
                'db_table': 'machine2part',
            },
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
            ],
            options={
                'db_table': 'owner',
            },
        ),
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
            ],
            options={
                'db_table': 'part',
            },
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('nickname', models.CharField(max_length=200)),
                ('questType', models.CharField(max_length=45)),
                ('statementHTML', models.TextField()),
                ('audioResource', models.CharField(max_length=100)),
                ('answer', models.TextField()),
                ('imageURL', models.TextField(max_length=200)),
                ('status', models.CharField(max_length=50)),
                ('standardId', models.CharField(max_length=45, null=True)),
                ('clusterId', models.CharField(max_length=45, null=True)),
                ('form', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='createTimestamp')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='modTimestamp')),
                ('authorNotes', models.TextField(null=True)),
                ('problemFormat', models.TextField()),
                ('usableAsExample', models.BooleanField()),
                ('creator', models.TextField(max_length=50)),
                ('lastModifier', models.TextField(max_length=50)),
                ('video', models.IntegerField()),
                ('example', models.IntegerField()),
                ('hasSnapshot', models.BooleanField()),
                ('language', models.CharField(default='english', max_length=10)),
            ],
            options={
                'db_table': 'problem',
            },
        ),
        migrations.CreateModel(
            name='ProblemAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('val', models.TextField()),
                ('choiceLetter', models.CharField(max_length=1)),
                ('hintText', models.CharField(max_length=200)),
                ('order', models.IntegerField()),
                ('bindingPosition', models.IntegerField()),
                ('problem', models.ForeignKey(db_column='probId', on_delete=django.db.models.deletion.PROTECT, to='msadmin.Problem')),
            ],
            options={
                'db_table': 'problemanswers',
            },
        ),
        migrations.CreateModel(
            name='ProblemDifficulty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diff_level', models.FloatField(db_column='diff_level')),
                ('totalProbs', models.IntegerField()),
                ('problem', models.ForeignKey(db_column='problemId', on_delete=django.db.models.deletion.PROTECT, to='msadmin.Problem')),
            ],
            options={
                'db_table': 'overallprobdifficulty',
            },
        ),
        migrations.CreateModel(
            name='ProblemLayout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('problemFormat', models.TextField()),
                ('name', models.CharField(max_length=45)),
                ('notes', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=150)),
            ],
            options={
                'db_table': 'problemlayout',
            },
        ),
        migrations.CreateModel(
            name='ProblemMediaFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=100)),
                ('hint', models.ForeignKey(db_column='hintId', null=True, on_delete=django.db.models.deletion.PROTECT, to='msadmin.Hint')),
                ('problem', models.ForeignKey(db_column='probId', on_delete=django.db.models.deletion.PROTECT, to='msadmin.Problem')),
            ],
            options={
                'db_table': 'problemmediafile',
            },
        ),
        migrations.CreateModel(
            name='ProblemStandardMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('probId', models.IntegerField()),
                ('stdId', models.CharField(max_length=12)),
                ('modtimestamp', models.DateTimeField(auto_now=True, db_column='modTimestamp')),
            ],
            options={
                'db_table': 'ProbStdMap',
            },
        ),
        migrations.CreateModel(
            name='ProblemTopicMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('problem', models.ForeignKey(db_column='probId', on_delete=django.db.models.deletion.PROTECT, to='msadmin.Problem')),
            ],
            options={
                'db_table': 'ProbProbGroup',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('url', models.CharField(max_length=100)),
                ('answer', models.CharField(max_length=100)),
                ('ansType', models.IntegerField()),
                ('aChoice', models.CharField(max_length=200)),
                ('bChoice', models.CharField(max_length=200)),
                ('cChoice', models.CharField(max_length=200)),
                ('dChoice', models.CharField(max_length=200)),
                ('eChoice', models.CharField(max_length=200)),
                ('aURL', models.CharField(max_length=100)),
                ('bURL', models.CharField(max_length=100)),
                ('cURL', models.CharField(max_length=100)),
                ('dURL', models.CharField(max_length=100)),
                ('eURL', models.CharField(max_length=100)),
                ('comment', models.CharField(max_length=100)),
                ('waitTimeSecs', models.IntegerField()),
                ('hoverText', models.CharField(max_length=150)),
                ('imageFilename', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'prepostproblem',
            },
        ),
        migrations.CreateModel(
            name='Ruleset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
            ],
            options={
                'db_table': 'ruleset',
            },
        ),
        migrations.CreateModel(
            name='SCISMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('config', models.TextField(blank=True, db_column='config')),
                ('isActive', models.BooleanField()),
                ('interventionSelector', models.ForeignKey(db_column='intervention_selector_id', on_delete=django.db.models.deletion.PROTECT, to='msadmin.InterventionSelector')),
            ],
            options={
                'db_table': 'sc_is_map',
            },
        ),
        migrations.CreateModel(
            name='SCParamMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField()),
            ],
            options={
                'db_table': 'sc_param_map',
            },
        ),
        migrations.CreateModel(
            name='Standard',
            fields=[
                ('id', models.CharField(max_length=12, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=1000)),
                ('grade', models.CharField(max_length=5)),
                ('category', models.CharField(max_length=150)),
                ('clusterName', models.CharField(max_length=800)),
                ('clusterId', models.IntegerField()),
                ('idABC', models.CharField(max_length=15)),
            ],
            options={
                'db_table': 'standard',
            },
        ),
        migrations.CreateModel(
            name='Strategy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('description', models.TextField()),
                ('aclass', models.ForeignKey(blank=True, db_column='classid', null=True, on_delete=django.db.models.deletion.PROTECT, to='msadmin.Class')),
                ('lc', models.ForeignKey(blank=True, db_column='lcid', null=True, on_delete=django.db.models.deletion.PROTECT, to='msadmin.LC')),
            ],
            options={
                'db_table': 'strategy',
            },
        ),
        migrations.CreateModel(
            name='StrategyComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('className', models.CharField(blank=True, choices=[('edu.umass.ckc.wo.tutor.model.TopicModel', 'TopicModel'), ('edu.umass.ckc.wo.tutor.model.CCLessonModel', 'CCLessonModel'), ('edu.umass.ckc.wo.tutor.pedModel.BasePedagogicalModel', 'BasePedagogicalModel'), ('edu.umass.ckc.wo.tutor.pedModel.SingleTopicPM', 'SingleTopicPedagogicalModel'), ('None', 'None')], max_length=100, null=True)),
                ('description', models.CharField(max_length=800)),
                ('briefDescr', models.CharField(max_length=200)),
                ('type', models.CharField(choices=[('login', 'login'), ('lesson', 'lesson'), ('tutor', 'tutor')], max_length=45)),
                ('is_generic', models.BooleanField()),
                ('interventionSelectors', models.ManyToManyField(through='msadmin.SCISMap', to='msadmin.InterventionSelector')),
            ],
            options={
                'db_table': 'strategy_component',
            },
        ),
        migrations.CreateModel(
            name='StrategyComponentParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('value', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=800)),
                ('isActive', models.BooleanField()),
                ('type', models.CharField(blank=True, max_length=45, null=True)),
                ('myStrategy', models.ForeignKey(blank=True, db_column='strategy_id', null=True, on_delete=django.db.models.deletion.PROTECT, to='msadmin.Strategy')),
            ],
            options={
                'db_table': 'sc_param',
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fname', models.CharField(db_column='fname', max_length=50)),
                ('lname', models.CharField(db_column='lname', max_length=50)),
            ],
            options={
                'db_table': 'teacher',
            },
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('isActive', models.BooleanField()),
            ],
            options={
                'db_table': 'preposttest',
            },
        ),
        migrations.CreateModel(
            name='TestQuestionMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField()),
                ('question', models.ForeignKey(db_column='probId', on_delete=django.db.models.deletion.PROTECT, related_name='link2Test', to='msadmin.Question')),
                ('test', models.ForeignKey(db_column='testId', on_delete=django.db.models.deletion.PROTECT, to='msadmin.Test')),
            ],
            options={
                'db_table': 'prepostproblemtestmap',
                'ordering': ('position',),
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('summary', models.CharField(max_length=100)),
                ('intro', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=5)),
            ],
            options={
                'db_table': 'ProblemGroup',
            },
        ),
        migrations.AddField(
            model_name='test',
            name='questions',
            field=models.ManyToManyField(through='msadmin.TestQuestionMap', to='msadmin.Question'),
        ),
        migrations.AddField(
            model_name='strategycomponent',
            name='params',
            field=models.ManyToManyField(through='msadmin.SCParamMap', to='msadmin.StrategyComponentParam'),
        ),
        migrations.AddField(
            model_name='strategy',
            name='lesson',
            field=models.ForeignKey(db_column='lesson_sc_id', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='StrategyLesson', to='msadmin.StrategyComponent'),
        ),
        migrations.AddField(
            model_name='strategy',
            name='login',
            field=models.ForeignKey(db_column='login_sc_id', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='StrategyLogin', to='msadmin.StrategyComponent'),
        ),
        migrations.AddField(
            model_name='strategy',
            name='tutor',
            field=models.ForeignKey(db_column='tutor_sc_id', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='StrategyTutor', to='msadmin.StrategyComponent'),
        ),
        migrations.AddField(
            model_name='scparammap',
            name='myStrategy',
            field=models.ForeignKey(blank=True, db_column='strategy_id', null=True, on_delete=django.db.models.deletion.PROTECT, to='msadmin.Strategy'),
        ),
        migrations.AddField(
            model_name='scparammap',
            name='param',
            field=models.ForeignKey(db_column='sc_param_id', on_delete=django.db.models.deletion.PROTECT, to='msadmin.StrategyComponentParam'),
        ),
        migrations.AddField(
            model_name='scparammap',
            name='strategyComponent',
            field=models.ForeignKey(db_column='strategy_component_id', on_delete=django.db.models.deletion.PROTECT, to='msadmin.StrategyComponent'),
        ),
        migrations.AddField(
            model_name='scismap',
            name='myStrategy',
            field=models.ForeignKey(blank=True, db_column='strategy_id', null=True, on_delete=django.db.models.deletion.PROTECT, to='msadmin.Strategy'),
        ),
        migrations.AddField(
            model_name='scismap',
            name='strategyComponent',
            field=models.ForeignKey(db_column='strategy_component_id', on_delete=django.db.models.deletion.PROTECT, to='msadmin.StrategyComponent'),
        ),
        migrations.AddField(
            model_name='problemtopicmap',
            name='topic',
            field=models.ForeignKey(db_column='pgroupid', on_delete=django.db.models.deletion.PROTECT, to='msadmin.Topic'),
        ),
        migrations.AddField(
            model_name='problem',
            name='audioFile',
            field=models.ForeignKey(db_column='audioFileId', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='msadmin.ProblemMediaFile'),
        ),
        migrations.AddField(
            model_name='problem',
            name='imageFile',
            field=models.ForeignKey(db_column='imageFileId', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='msadmin.ProblemMediaFile'),
        ),
        migrations.AddField(
            model_name='problem',
            name='layout',
            field=models.ForeignKey(db_column='layoutID', null=True, on_delete=django.db.models.deletion.PROTECT, to='msadmin.FormatTemplate'),
        ),
        migrations.AddField(
            model_name='machine2part',
            name='part',
            field=models.ForeignKey(db_column='partId', on_delete=django.db.models.deletion.PROTECT, to='msadmin.Part'),
        ),
        migrations.AddField(
            model_name='machine2owner',
            name='owner',
            field=models.ForeignKey(db_column='ownerId', on_delete=django.db.models.deletion.PROTECT, to='msadmin.Owner'),
        ),
        migrations.AddField(
            model_name='machine',
            name='owner',
            field=models.ManyToManyField(through='msadmin.Machine2Owner', to='msadmin.Owner'),
        ),
        migrations.AddField(
            model_name='machine',
            name='parts',
            field=models.ManyToManyField(through='msadmin.Machine2Part', to='msadmin.Part'),
        ),
        migrations.AddField(
            model_name='lc2ruleset',
            name='ruleset',
            field=models.ForeignKey(db_column='rulesetid', on_delete=django.db.models.deletion.PROTECT, to='msadmin.Ruleset'),
        ),
        migrations.AddField(
            model_name='lc',
            name='rulesets',
            field=models.ManyToManyField(through='msadmin.LC2Ruleset', to='msadmin.Ruleset'),
        ),
        migrations.AddField(
            model_name='interventionselectorparam',
            name='baseParam',
            field=models.ForeignKey(db_column='paramid', on_delete=django.db.models.deletion.PROTECT, to='msadmin.ISParamBase'),
        ),
        migrations.AddField(
            model_name='interventionselectorparam',
            name='myStrategy',
            field=models.ForeignKey(db_column='strategy_id', null=True, on_delete=django.db.models.deletion.PROTECT, to='msadmin.Strategy'),
        ),
        migrations.AddField(
            model_name='interventionselectorparam',
            name='scismap',
            field=models.ForeignKey(db_column='sc_is_map_id', on_delete=django.db.models.deletion.PROTECT, to='msadmin.SCISMap', verbose_name='StrategyComponent:InterventionSelector'),
        ),
        migrations.AddField(
            model_name='interventionselector',
            name='myStrategy',
            field=models.ForeignKey(blank=True, db_column='strategy_id', null=True, on_delete=django.db.models.deletion.PROTECT, to='msadmin.Strategy'),
        ),
        migrations.AddField(
            model_name='hint',
            name='audioFile',
            field=models.ForeignKey(db_column='audioFileId', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='msadmin.ProblemMediaFile'),
        ),
        migrations.AddField(
            model_name='hint',
            name='imageFile',
            field=models.ForeignKey(db_column='imageFileId', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='msadmin.ProblemMediaFile'),
        ),
        migrations.AddField(
            model_name='hint',
            name='problem',
            field=models.ForeignKey(db_column='problemId', on_delete=django.db.models.deletion.PROTECT, to='msadmin.Problem'),
        ),
        migrations.AlterUniqueTogether(
            name='testquestionmap',
            unique_together={('question', 'test')},
        ),
    ]
