Within the msadmin tool that allows us to configure intervention selectors within a tutoring strategy we want
 the pretest and posttest interventions to allow us to set a parameter called preposttestName to be the name of the pre or post
 test that they will be using (the name column in the preposttest table is what this refers to).   So this allows us
 to select a particular pre or post test for a given class rather than have to get it from the classconfig table.

 The difficulty here is that most parameters for a intervention selectors are a simple set of fixed values (e.g. true, false)
 but these are a set of names that come from the preposttest table which is possibly changing (adds, deletes, updates).
 This meant adding some triggers to the preposttest table so that when a new test is added, we add rows to the table
 that stores legal values for intervention selector params (is_param_values).   So here are MySQL triggers in case I ever need
 to mess with this again:
To drop triggers:
drop trigger param_value_after_ins_trig;
drop trigger param_value_after_upd_trig;
drop trigger param_value_after_del_trig;

Add the triggers to the preposttest table:

 delimiter #
 create trigger param_value_after_ins_trig after insert on preposttest
 for each row
 begin
 if new.isActive = 1 then
 insert into is_param_value (value, isparamId) values (new.name, (select id from is_param_base where name='preposttestName' and intervention_selector_id=(select id from intervention_selector where name='Pretest')) );
 insert into is_param_value (value, isparamId) values (new.name, (select id from is_param_base where name='preposttestName' and intervention_selector_id=(select id from intervention_selector where name='Posttest')));
 end if;
 end


 create trigger param_value_after_upd_trig after update on preposttest
 for each row
 begin
 if new.isActive = 1 and old.isActive = 0 then
 insert into is_param_value (value, isparamId) values (new.name, (select id from is_param_base where name='preposttestName' and intervention_selector_id=(select id from intervention_selector where name='Pretest')) );
 insert into is_param_value (value, isparamId) values (new.name, (select id from is_param_base where name='preposttestName' and intervention_selector_id=(select id from intervention_selector where name='Posttest')));
 elseif new.isActive = 0 and old.isActive = 1 then
 delete from is_param_value where value=old.name and isParamId=(select id from is_param_base where name='preposttestName' and intervention_selector_id=(select id from intervention_selector where name='Pretest')) ;
 delete from is_param_value where value=old.name and isParamId=(select id from is_param_base where name='preposttestName' and intervention_selector_id=(select id from intervention_selector where name='Posttest')) ;
 elseif new.isActive = 1 and new.name != old.name then
 update is_param_value set value = new.name where isparamId=(select id from is_param_base where name='preposttestName' and intervention_selector_id=(select id from intervention_selector where name='Pretest')) ;
 update is_param_value set value = new.name where isparamId=(select id from is_param_base where name='preposttestName' and intervention_selector_id=(select id from intervention_selector where name='Posttest'));
 end if;

 end


 create trigger param_value_after_del_trig after delete on preposttest
 for each row
 begin
 delete from is_param_value where value=old.name and isParamId=(select id from is_param_base where name='preposttestName' and intervention_selector_id=(select id from intervention_selector where name='Pretest')) ;
 delete from is_param_value where value=old.name and isParamId=(select id from is_param_base where name='preposttestName' and intervention_selector_id=(select id from intervention_selector where name='Posttest')) ;

 end
delimiter ;