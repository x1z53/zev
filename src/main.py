from dataclasses import dataclass
import dotenv
import typer
import os
from utils import get_input_string
from llm import get_options
import questionary
import pyperclip
from rich import print as rprint

app = typer.Typer()


@dataclass
class DotEnvField:
    name: str
    prompt: str
    required: bool = True
    default: str = ""


@app.command()
def setup():
    dotenv_fields = [
        DotEnvField(
            name="OPENAI_API_KEY",
            prompt="Enter your OpenAI API key",
            required=False,
            default="",
        ),
    ]

    if os.path.exists(".env"):
        typer.echo("Creating a new .env file")
        for field in dotenv_fields:
            os.environ[field.name] = ""

    dotenv.load_dotenv()
    new_file = ""
    for field in dotenv_fields:
        current_value = os.getenv(field.name)
        print("Current value: ", current_value)
        new_value = get_input_string(field.name, field.prompt, current_value, field.default, field.required)
        new_file += f"{field.name}={new_value}\n"

    with open(".env", "w") as f:
        f.write(new_file)


def show_options(words: str):
    response = get_options(words)
    if not response.is_valid:
        print(response.explanation_if_not_valid)
        return

    if not response.commands:
        print("No commands available")
        return

    options = [questionary.Choice(cmd.command, description=cmd.short_explanation) for cmd in response.commands]
    options.append(questionary.Choice("Cancel"))
    options.append(questionary.Separator())

    selected = questionary.select(
        "Select command:",
        choices=options,
        use_shortcuts=True,
        style=questionary.Style(
            [
                ("answer", "fg:#61afef"),
                ("question", "bold"),
                ("instruction", "fg:#98c379"),
            ]
        ),
    ).ask()

    if selected != "Cancel":
        pyperclip.copy(selected)
        rprint(f"\n[green]✓[/green] Copied to clipboard")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context, words: list[str] = typer.Argument(None)):
    if not ctx.invoked_subcommand:
        if not words:
            return
        if words[0] in ctx.command.commands:
            command = ctx.command.commands[words[0]]
            command(words[1:] if len(words) > 1 else [])
        else:
            show_options(" ".join(words))


if __name__ == "__main__":
    app()
