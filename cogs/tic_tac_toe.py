import discord
from discord.ext import commands
from discord import app_commands
import os

# Board positions for reference:
# 0 | 1 | 2
# 3 | 4 | 5
# 6 | 7 | 8

class TicTacToe(discord.ui.View):
    def __init__(self, ctx, channel_id):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.ctx = ctx
        self.channel_id = channel_id
        self.board = [' ']*9
        self.current_turn = "X"  # User is X
        self.game_over = False
        self.message = None

    def check_winner(self, mark):
        wins = [
            [0,1,2], [3,4,5], [6,7,8],  # rows
            [0,3,6], [1,4,7], [2,5,8],  # cols
            [0,4,8], [2,4,6]            # diagonals
        ]
        for combo in wins:
            if all(self.board[i] == mark for i in combo):
                return True
        return False

    def is_draw(self):
        return all(space != ' ' for space in self.board)

    def bot_move(self):
        # Simple bot AI: pick first available spot
        for i in range(9):
            if self.board[i] == ' ':
                self.board[i] = 'O'
                return i

    def render_board(self):
        # Return a string representation of the board
        def mark(i):
            return self.board[i] if self.board[i] != ' ' else str(i+1)
        line = "-------------"
        board_str = (
            f"{mark(0)} | {mark(1)} | {mark(2)}\n"
            f"{line}\n"
            f"{mark(3)} | {mark(4)} | {mark(5)}\n"
            f"{line}\n"
            f"{mark(6)} | {mark(7)} | {mark(8)}"
        )
        return "```\n" + board_str + "\n```"

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Only allow user who started to interact
        return interaction.user == self.ctx.author

    async def disable_all_buttons(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            await self.message.edit(view=self)

    @discord.ui.button(label="1", style=discord.ButtonStyle.secondary, row=0)
    async def button1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.player_move(interaction, 0)

    @discord.ui.button(label="2", style=discord.ButtonStyle.secondary, row=0)
    async def button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.player_move(interaction, 1)

    @discord.ui.button(label="3", style=discord.ButtonStyle.secondary, row=0)
    async def button3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.player_move(interaction, 2)

    @discord.ui.button(label="4", style=discord.ButtonStyle.secondary, row=1)
    async def button4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.player_move(interaction, 3)

    @discord.ui.button(label="5", style=discord.ButtonStyle.secondary, row=1)
    async def button5(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.player_move(interaction, 4)

    @discord.ui.button(label="6", style=discord.ButtonStyle.secondary, row=1)
    async def button6(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.player_move(interaction, 5)

    @discord.ui.button(label="7", style=discord.ButtonStyle.secondary, row=2)
    async def button7(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.player_move(interaction, 6)

    @discord.ui.button(label="8", style=discord.ButtonStyle.secondary, row=2)
    async def button8(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.player_move(interaction, 7)

    @discord.ui.button(label="9", style=discord.ButtonStyle.secondary, row=2)
    async def button9(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.player_move(interaction, 8)

    async def player_move(self, interaction, pos):
        if self.game_over:
            await interaction.response.send_message("Game is already over!", ephemeral=True)
            return
        if self.board[pos] != ' ':
            await interaction.response.send_message("That spot is already taken!", ephemeral=True)
            return

        self.board[pos] = 'X'

        if self.check_winner('X'):
            self.game_over = True
            await self.disable_all_buttons()
            await interaction.response.edit_message(content=f"You win! 🎉\n{self.render_board()}", view=self)
            return

        if self.is_draw():
            self.game_over = True
            await self.disable_all_buttons()
            await interaction.response.edit_message(content=f"It's a draw!\n{self.render_board()}", view=self)
            return

        # Bot move
        bot_pos = self.bot_move()

        if self.check_winner('O'):
            self.game_over = True
            await self.disable_all_buttons()
            await interaction.response.edit_message(content=f"I win! 🤖\n{self.render_board()}", view=self)
            return

        if self.is_draw():
            self.game_over = True
            await self.disable_all_buttons()
            await interaction.response.edit_message(content=f"It's a draw!\n{self.render_board()}", view=self)
            return

        # Update buttons to disable taken spots
        self.children[bot_pos].disabled = True
        self.children[pos].disabled = True

        await interaction.response.edit_message(content=f"Your turn! You are X.\n{self.render_board()}", view=self)

class TicTacToeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = int(os.getenv("TICTACTOE_CHANNEL_ID", 0))
        self.active_games = {}

    @commands.command(name="tictactoe", aliases=["ttt"])
    async def tictactoe(self, ctx):
        if self.channel_id and ctx.channel.id != self.channel_id:
            await ctx.send(f"This command can only be used in <#{self.channel_id}>.")
            return

        if ctx.author.id in self.active_games:
            await ctx.send("You already have an active game! Finish it before starting a new one.")
            return

        view = TicTacToe(ctx, self.channel_id)
        msg = await ctx.send(f"Let's play Tic-Tac-Toe! You are X.\n{view.render_board()}", view=view)
        view.message = msg
        self.active_games[ctx.author.id] = view

        # Remove game from active after timeout
        def remove_game(view):
            self.active_games.pop(ctx.author.id, None)

        view.on_timeout = lambda: remove_game(view)

async def setup(bot):
    await bot.add_cog(TicTacToeCog(bot))
