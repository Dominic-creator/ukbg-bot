import discord
from discord import app_commands
from discord.ui import Modal, TextInput, View
import os

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ----- Modal für Termin -----
class TerminModal(Modal, title="Termin anfragen"):
    name = TextInput(label="Ihr Name", style=discord.TextStyle.short, required=True)
    email = TextInput(label="Ihre E-Mail", style=discord.TextStyle.short, required=True)
    abteilung = TextInput(label="Abteilung", style=discord.TextStyle.short, required=True)
    datum = TextInput(label="Wunschtermin (TT.MM.JJJJ)", style=discord.TextStyle.short, required=False)
    nachricht = TextInput(label="Nachricht / Anliegen", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        channel = client.get_channel(CHANNEL_ID)
        embed = discord.Embed(
            title="📅 Neue Terminanfrage – Campus Nord",
            color=0x3498db
        )
        embed.add_field(name="👤 Name", value=self.name.value, inline=False)
        embed.add_field(name="📧 E-Mail", value=self.email.value, inline=False)
        embed.add_field(name="🏥 Abteilung", value=self.abteilung.value, inline=False)
        embed.add_field(name="📅 Wunschtermin", value=self.datum.value or "Nicht angegeben", inline=False)
        embed.add_field(name="📝 Nachricht", value=self.nachricht.value or "Keine Nachricht", inline=False)
        embed.set_footer(text=f"Anfrage von {interaction.user}")

        # Buttons für Bestätigung und Ablehnung
        class TerminButtons(View):
            def __init__(self, original_user_id, abteilung_value, datum_value):
                super().__init__(timeout=None)
                self.original_user_id = original_user_id
                self.abteilung_value = abteilung_value
                self.datum_value = datum_value
            
            @discord.ui.button(label="Termin bestätigen", style=discord.ButtonStyle.success, emoji="✅")
            async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
                try:
                    # DM an den ursprünglichen Anfragesteller
                    original_user = await client.fetch_user(self.original_user_id)
                    await original_user.send(f"✅ **Termin bestätigt!**\n\nIhr Termin bei der Abteilung **{self.abteilung_value}** wurde bestätigt!\n\n📅 Wunschtermin: {self.datum_value or 'Wird noch bekannt gegeben'}")
                    
                    # Embed aktualisieren
                    embed.color = 0x2ecc71
                    embed.title = "📅 Terminanfrage – Campus Nord ✅ **BESTÄTIGT**"
                    await interaction.response.edit_message(embed=embed, view=None)
                    
                except Exception as e:
                    await interaction.response.send_message(f"Fehler beim Bestätigen: {e}", ephemeral=True)
            
            @discord.ui.button(label="Termin ablehnen", style=discord.ButtonStyle.danger, emoji="❌")
            async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
                try:
                    # DM an den ursprünglichen Anfragesteller
                    original_user = await client.fetch_user(self.original_user_id)
                    await original_user.send(f"❌ **Termin abgelehnt**\n\nIhr Termin bei der Abteilung **{self.abteilung_value}** konnte leider nicht bestätigt werden.\n\nBitte wenden Sie sich für alternative Termine direkt an die Abteilung.")
                    
                    # Embed aktualisieren
                    embed.color = 0xe74c3c
                    embed.title = "📅 Terminanfrage – Campus Nord ❌ **ABGELEHNT**"
                    await interaction.response.edit_message(embed=embed, view=None)
                    
                except Exception as e:
                    await interaction.response.send_message(f"Fehler beim Ablehnen: {e}", ephemeral=True)

        message = await channel.send(embed=embed, view=TerminButtons(interaction.user.id, self.abteilung.value, self.datum.value))
        await interaction.response.send_message("✅ Ihre Anfrage wurde gesendet!", ephemeral=True)

# ----- Slash-Befehl /termin -----
@tree.command(name="termin", description="Termin am Campus Nord anfragen")
async def termin_command(interaction: discord.Interaction):
    await interaction.response.send_modal(TerminModal())

# ----- Bot ready -----
@client.event
async def on_ready():
    await tree.sync()
    print(f"{client.user} ist online und bereit!")

client.run(TOKEN)
