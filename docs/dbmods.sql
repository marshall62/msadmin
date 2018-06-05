ALTER TABLE `wayangoutpostdb`.`is_param_sc`
ADD COLUMN `strategy_id` INT NULL AFTER `isActive`,
ADD INDEX `fk_is_param_sc_3_idx` (`strategy_id` ASC);
ALTER TABLE `wayangoutpostdb`.`is_param_sc`
ADD CONSTRAINT `fk_is_param_sc_3`
  FOREIGN KEY (`strategy_id`)
  REFERENCES `wayangoutpostdb`.`strategy` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


ALTER TABLE `wayangoutpostdb`.`intervention_selector`
ADD COLUMN `strategy_id` INT NULL AFTER `briefDescription`,
ADD INDEX `fk_intervention_selector_1_idx` (`strategy_id` ASC);
ALTER TABLE `wayangoutpostdb`.`intervention_selector`
ADD CONSTRAINT `fk_intervention_selector_1`
  FOREIGN KEY (`strategy_id`)
  REFERENCES `wayangoutpostdb`.`strategy` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;

ALTER TABLE `wayangoutpostdb`.`sc_param_map`
ADD COLUMN `strategy_id` INT NULL AFTER `id`,
ADD INDEX `fk_sc_param_map_1_idx` (`strategy_id` ASC);
ALTER TABLE `wayangoutpostdb`.`sc_param_map`
ADD CONSTRAINT `fk_sc_param_map_1`
  FOREIGN KEY (`strategy_id`)
  REFERENCES `wayangoutpostdb`.`strategy` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


ALTER TABLE `wayangoutpostdb`.`sc_is_map`
ADD COLUMN `strategy_id` INT NULL AFTER `config`,
ADD INDEX `fk_sc_is_map_1_idx` (`strategy_id` ASC);
ALTER TABLE `wayangoutpostdb`.`sc_is_map`
ADD CONSTRAINT `fk_sc_is_map_1`
  FOREIGN KEY (`strategy_id`)
  REFERENCES `wayangoutpostdb`.`strategy` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;

ALTER TABLE `wayangoutpostdb`.`strategy`
ADD COLUMN `classid` INT NULL AFTER `description`,
ADD INDEX `fk_strategy_1_idx` (`classid` ASC);
ALTER TABLE `wayangoutpostdb`.`strategy`
ADD CONSTRAINT `fk_strategy_1`
  FOREIGN KEY (`classid`)
  REFERENCES `wayangoutpostdb`.`class` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;

ALTER TABLE `wayangoutpostdb`.`sc_param`
ADD COLUMN `isactive` TINYINT NULL AFTER `description`;

ALTER TABLE `wayangoutpostdb`.`sc_param`
ADD COLUMN `strategy_id` INT NULL AFTER `isactive`,
ADD INDEX `fk_sc_param_1_idx` (`strategy_id` ASC);

ALTER TABLE `wayangoutpostdb`.`sc_param`
ADD CONSTRAINT `fk_sc_param_1`
  FOREIGN KEY (`strategy_id`)
  REFERENCES `wayangoutpostdb`.`strategy` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;

ALTER TABLE `wayangoutpostdb`.`strategy`
DROP FOREIGN KEY `fk_strategy_lesson_sc`,
DROP FOREIGN KEY `fk_strategy_login_sc`,
DROP FOREIGN KEY `fk_strategy_tutor_sc`;
ALTER TABLE `wayangoutpostdb`.`strategy`
CHANGE COLUMN `lesson_sc_id` `lesson_sc_id` INT(11) NULL ,
CHANGE COLUMN `login_sc_id` `login_sc_id` INT(11) NULL ,
CHANGE COLUMN `tutor_sc_id` `tutor_sc_id` INT(11) NULL ;
ALTER TABLE `wayangoutpostdb`.`strategy`
ADD CONSTRAINT `fk_strategy_lesson_sc`
  FOREIGN KEY (`lesson_sc_id`)
  REFERENCES `wayangoutpostdb`.`strategy_component` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_strategy_login_sc`
  FOREIGN KEY (`login_sc_id`)
  REFERENCES `wayangoutpostdb`.`strategy_component` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_strategy_tutor_sc`
  FOREIGN KEY (`tutor_sc_id`)
  REFERENCES `wayangoutpostdb`.`strategy_component` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;

ALTER TABLE `wayangoutpostdb`.`sc_is_map`
ADD COLUMN `isActive` TINYINT NULL AFTER `strategy_id`;


ALTER TABLE `wayangoutpostdb`.`intervention_selector`
ADD COLUMN `generic_is_id` INT NULL AFTER `type`,
ADD INDEX `fk_intervention_selector_2_idx` (`generic_is_id` ASC);
ALTER TABLE `wayangoutpostdb`.`intervention_selector`
ADD CONSTRAINT `fk_intervention_selector_2`
  FOREIGN KEY (`generic_is_id`)
  REFERENCES `wayangoutpostdb`.`intervention_selector` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;

ALTER TABLE `wayangoutpostdb`.`strategy_component`
CHANGE COLUMN `className` `className` VARCHAR(100) NULL ;


ALTER TABLE `wayangoutpostdb`.`intervention_selector`
ADD COLUMN `type` VARCHAR(10) NULL AFTER `strategy_id`;

UPDATE `wayangoutpostdb`.`intervention_selector` SET `type`='lesson' WHERE `id`='1';
UPDATE `wayangoutpostdb`.`intervention_selector` SET `type`='lesson' WHERE `id`='5';
UPDATE `wayangoutpostdb`.`intervention_selector` SET `type`='lesson' WHERE `id`='6';
UPDATE `wayangoutpostdb`.`intervention_selector` SET `type`='login' WHERE `id`='2';
UPDATE `wayangoutpostdb`.`intervention_selector` SET `type`='login' WHERE `id`='3';
UPDATE `wayangoutpostdb`.`intervention_selector` SET `type`='login' WHERE `id`='4';
UPDATE `wayangoutpostdb`.`intervention_selector` SET `type`='login' WHERE `id`='8';
UPDATE `wayangoutpostdb`.`intervention_selector` SET `type`='login' WHERE `id`='9';
UPDATE `wayangoutpostdb`.`intervention_selector` SET `type`='login' WHERE `id`='27';
UPDATE `wayangoutpostdb`.`intervention_selector` SET `type`='tutor' WHERE `id`='21';
UPDATE `wayangoutpostdb`.`intervention_selector` SET `type`='tutor' WHERE `id`='22';
UPDATE `wayangoutpostdb`.`intervention_selector` SET `type`='tutor' WHERE `id`='23';
UPDATE `wayangoutpostdb`.`intervention_selector` SET `type`='tutor' WHERE `id`='28';
UPDATE `wayangoutpostdb`.`intervention_selector` SET `type`='tutor' WHERE `id`='29';
UPDATE `wayangoutpostdb`.`intervention_selector` SET `type`='tutor' WHERE `id`='30';


ALTER TABLE `wayangoutpostdb`.`strategy`
DROP FOREIGN KEY `fk_strategy_lesson_sc`,
DROP FOREIGN KEY `fk_strategy_login_sc`,
DROP FOREIGN KEY `fk_strategy_tutor_sc`;
ALTER TABLE `wayangoutpostdb`.`strategy`
ADD CONSTRAINT `fk_strategy_lesson_sc`
  FOREIGN KEY (`lesson_sc_id`)
  REFERENCES `wayangoutpostdb`.`strategy_component` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE,
ADD CONSTRAINT `fk_strategy_login_sc`
  FOREIGN KEY (`login_sc_id`)
  REFERENCES `wayangoutpostdb`.`strategy_component` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE,
ADD CONSTRAINT `fk_strategy_tutor_sc`
  FOREIGN KEY (`tutor_sc_id`)
  REFERENCES `wayangoutpostdb`.`strategy_component` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

ALTER TABLE `wayangoutpostdb`.`sc_param_map`
DROP FOREIGN KEY `fk_sc_param_map_1`,
DROP FOREIGN KEY `fk_sc_param_map_sc_param`,
DROP FOREIGN KEY `fk_sc_param_map_strategy_component`;
ALTER TABLE `wayangoutpostdb`.`sc_param_map`
ADD CONSTRAINT `fk_sc_param_map_1`
  FOREIGN KEY (`strategy_id`)
  REFERENCES `wayangoutpostdb`.`strategy` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE,
ADD CONSTRAINT `fk_sc_param_map_sc_param`
  FOREIGN KEY (`sc_param_id`)
  REFERENCES `wayangoutpostdb`.`sc_param` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE,
ADD CONSTRAINT `fk_sc_param_map_strategy_component`
  FOREIGN KEY (`strategy_component_id`)
  REFERENCES `wayangoutpostdb`.`strategy_component` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

ALTER TABLE `wayangoutpostdb`.`sc_param`
DROP FOREIGN KEY `fk_sc_param_1`;
ALTER TABLE `wayangoutpostdb`.`sc_param`
ADD CONSTRAINT `fk_sc_param_1`
  FOREIGN KEY (`strategy_id`)
  REFERENCES `wayangoutpostdb`.`strategy` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

ALTER TABLE `wayangoutpostdb`.`sc_is_map`
DROP FOREIGN KEY `fk_sc_is_map_1`,
DROP FOREIGN KEY `fk_sc_is_map_intervention_selector`,
DROP FOREIGN KEY `fk_sc_is_map_strategy_component`;
ALTER TABLE `wayangoutpostdb`.`sc_is_map`
ADD CONSTRAINT `fk_sc_is_map_1`
  FOREIGN KEY (`strategy_id`)
  REFERENCES `wayangoutpostdb`.`strategy` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE,
ADD CONSTRAINT `fk_sc_is_map_intervention_selector`
  FOREIGN KEY (`intervention_selector_id`)
  REFERENCES `wayangoutpostdb`.`intervention_selector` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE,
ADD CONSTRAINT `fk_sc_is_map_strategy_component`
  FOREIGN KEY (`strategy_component_id`)
  REFERENCES `wayangoutpostdb`.`strategy_component` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

ALTER TABLE `wayangoutpostdb`.`intervention_selector`
DROP FOREIGN KEY `fk_intervention_selector_1`,
DROP FOREIGN KEY `fk_intervention_selector_2`;
ALTER TABLE `wayangoutpostdb`.`intervention_selector`
ADD CONSTRAINT `fk_intervention_selector_1`
  FOREIGN KEY (`strategy_id`)
  REFERENCES `wayangoutpostdb`.`strategy` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE,
ADD CONSTRAINT `fk_intervention_selector_2`
  FOREIGN KEY (`generic_is_id`)
  REFERENCES `wayangoutpostdb`.`intervention_selector` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

ALTER TABLE `wayangoutpostdb`.`is_param_sc`
DROP FOREIGN KEY `fk_is_param_sc_2`,
DROP FOREIGN KEY `fk_is_param_sc_3`;
ALTER TABLE `wayangoutpostdb`.`is_param_sc`
ADD CONSTRAINT `fk_is_param_sc_2`
  FOREIGN KEY (`sc_is_map_id`)
  REFERENCES `wayangoutpostdb`.`sc_is_map` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE,
ADD CONSTRAINT `fk_is_param_sc_3`
  FOREIGN KEY (`strategy_id`)
  REFERENCES `wayangoutpostdb`.`strategy` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE;




