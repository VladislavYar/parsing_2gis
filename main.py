from parser import Parser
from gui import GUI
from command_line import parser_command_line


def main() -> None:
    arg_parser = parser_command_line()
    args = arg_parser.parse_args()
    if args.gui:
        GUI()
        return
    parser = Parser()
    parser.VALIDATE_NAME_CITY = args.name
    parser.SLUG_CITY = args.slug
    parser.parsing()


if '__main__' == __name__:
    main()
