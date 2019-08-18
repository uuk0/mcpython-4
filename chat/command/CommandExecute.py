"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk

orginal game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import chat.command.Command
from chat.command.Command import SubCommand, ParseBridge, ParseType, ParseMode


@G.commandhandler
class CommandExecute(chat.command.Command.Command):
    @staticmethod
    def insert_parse_bridge(parsebridge: ParseBridge):
        # missing: align, anchored, facing, in
        execute_as = SubCommand(ParseType.DEFINIED_STRING, "as", mode=ParseMode.OPTIONAL).add_subcommand(
            SubCommand(ParseType.SELECTOR))
        execute_at = SubCommand(ParseType.DEFINIED_STRING, "at", mode=ParseMode.OPTIONAL).add_subcommand(
            SubCommand(ParseType.POSITION))
        # missing: blocks, data, score
        execute_if = SubCommand(ParseType.DEFINIED_STRING, "if", mode=ParseMode.OPTIONAL).add_subcommand(
            SubCommand(ParseType.DEFINIED_STRING, "block").add_subcommand(
                SubCommand(ParseType.POSITION).add_subcommand(ParseType.BLOCKNAME)
            )
        ).add_subcommand(
            SubCommand(ParseType.DEFINIED_STRING, "entity").add_subcommand(
                SubCommand(ParseType.SELECTOR)
            )
        )
        execute_run = SubCommand(ParseType.DEFINIED_STRING, "run", mode=ParseMode.OPTIONAL).add_subcommand(
            SubCommand(ParseType.OPEN_END_UNDEFINITED_STRING, min=1)
        )
        execute_unless = SubCommand(ParseType.DEFINIED_STRING, "unless", mode=ParseMode.OPTIONAL)
        execute_unless.sub_commands = execute_if.sub_commands
        sub_commands = [execute_as, execute_at, execute_if, execute_run]
        sub_commands_ends = [execute_as.sub_commands[0], execute_at.sub_commands[0],
                             execute_if.sub_commands[0].sub_commands[0].sub_commands[0],
                             execute_if.sub_commands[1].sub_commands[0],
                             execute_unless.sub_commands[0].sub_commands[0].sub_commands[0],
                             execute_unless.sub_commands[1].sub_commands[0]]
        for subcommand in sub_commands_ends + [parsebridge]:
            subcommand.sub_commands = sub_commands
        parsebridge.main_entry = "execute"

    @staticmethod
    def parse(values: list, modes: list, info):
        index = 0
        CommandExecute._parse_subcommand(index, values[index], values, info)

    @staticmethod
    def _parse_subcommand(index, command, values, info):
        if command == "as":
            index += 2
            for entity in values[index+1]:
                info.entity = entity
                CommandExecute._parse_subcommand(index, values[index], values, info)
            return
        elif command == "at":
            index += 2
            for position in values[index + 1]:
                info.position = position
                CommandExecute._parse_subcommand(index, values[index], values, info)
            return
        elif command in ["if", "unless"]:
            subcommand: str = values[index+1]
            index += 2
            flag = None
            if subcommand == "block":
                position, name = values[index], values[index+1]
                index += 2
                if position in G.world.world:
                    block = G.world.world[position]
                    flag = block.get_name() == G.blockhandler.blocks[name].get_name()
                else:
                    flag = name in ["air", "minecraft:air", None, 0]
            elif subcommand == "entity":
                selector = values[index]
                index += 1
                flag = len(selector) > 0

            if command == "if" and not flag: return
            if command == "unless" and flag: return

        elif command == "run":
            G.commandparser.parse("/"+" ".join(values[index+1]), info=info)
            index += 2

        if len(values) > index:
            CommandExecute._parse_subcommand(index, values[index], values, info)

    @staticmethod
    def get_help() -> list:
        return ["/execute \\as <selector>\\at <position>\\if / unless \\block <position> <blockname>\\entity <selector>"
                "\\ \\ run <command>: execute command with given arguments"]
