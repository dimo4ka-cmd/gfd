import discord
from discord import app_commands
from discord.ui import Modal, TextInput, Button, View
import asyncio

# Настройка интентов
intents = discord.Intents.default()
intents.members = True  # Для доступа к данным участников сервера
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Модальное окно для команды /увольнение
class DismissalModal(Modal, title="Увольнение"):
    dismissed_tag = TextInput(label="Тег увольняемого (@user)", placeholder="@username")
    reason = TextInput(label="Причина увольнения", style=discord.TextStyle.paragraph)
    rank = TextInput(label="С какого ранга увольняют", placeholder="Название роли")

    async def on_submit(self, interaction: discord.Interaction):
        # Получение никнейма увольняемого
        try:
            dismissed_id = int(self.dismissed_tag.value.replace("<@", "").replace(">", ""))
            dismissed_member = interaction.guild.get_member(dismissed_id)
            if not dismissed_member:
                await interaction.response.send_message("Участник не найден на сервере.", ephemeral=True)
                return
            dismissed_nickname = dismissed_member.display_name
        except ValueError:
            await interaction.response.send_message("Неверный формат тега увольняемого. Укажите @username.", ephemeral=True)
            return

        # Получение никнейма того, кто увольняет
        dismissing_member = interaction.user
        dismissing_nickname = dismissing_member.display_name

        # Создание embed-сообщения
        embed = discord.Embed(title="Увольнение", color=discord.Color.red())
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/123456789012345678.png")  # Замените на URL иконки, если есть
        embed.add_field(name="Увольняемый:", value=f"{self.dismissed_tag.value}\n**Ник:** {dismissed_nickname}", inline=True)
        embed.add_field(name="Увольняет:", value=f"{dismissing_member.mention}\n**Ник:** {dismissing_nickname}", inline=True)
        embed.add_field(name="Причина:", value=self.reason.value, inline=False)
        embed.add_field(name="С какого ранга:", value=self.rank.value, inline=False)
        embed.set_footer(text="Выберите действие ниже:")

        # Создание кнопок
        view = DismissalView(dismissed_member)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)

# Кнопки для команды /увольнение
class DismissalView(View):
    def __init__(self, member: discord.Member):
        super().__init__()
        self.member = member

    @discord.ui.button(label="Кикнуть", style=discord.ButtonStyle.danger, emoji="🚪")
    async def kick_button(self, interaction: discord.Interaction, button: Button):
        if self.member:
            try:
                await self.member.kick(reason="Увольнение")
                await interaction.response.send_message(f"{self.member.mention} был кикнут.", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("У бота недостаточно прав для кика участника.", ephemeral=True)
        else:
            await interaction.response.send_message("Участник не найден.", ephemeral=True)

    @discord.ui.button(label="Снять роли", style=discord.ButtonStyle.secondary, emoji="🛑")
    async def remove_roles_button(self, interaction: discord.Interaction, button: Button):
        if self.member:
            try:
                await self.member.edit(roles=[])
                await interaction.response.send_message(f"У {self.member.mention} сняты все роли.", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("У бота недостаточно прав для управления ролями.", ephemeral=True)
        else:
            await interaction.response.send_message("Участник не найден.", ephemeral=True)

# Модальное окно для команды /принятие
class AcceptanceModal(Modal, title="Принятие"):
    accepted_tag = TextInput(label="Тег принимаемого (@user)", placeholder="@username")
    acceptor_tag = TextInput(label="Тег принимающего (@user)", placeholder="@username")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            accepted_id = int(self.accepted_tag.value.replace("<@", "").replace(">", ""))
            accepted_member = interaction.guild.get_member(accepted_id)
            if not accepted_member:
                await interaction.response.send_message("Участник (принимаемый) не найден на сервере.", ephemeral=True)
                return
            accepted_nickname = accepted_member.display_name
        except ValueError:
            await interaction.response.send_message("Неверный формат тега принимаемого. Укажите @username.", ephemeral=True)
            return

        try:
            acceptor_id = int(self.acceptor_tag.value.replace("<@", "").replace(">", ""))
            acceptor_member = interaction.guild.get_member(acceptor_id)
            if not acceptor_member:
                await interaction.response.send_message("Участник (принимающий) не найден на сервере.", ephemeral=True)
                return
            acceptor_nickname = acceptor_member.display_name
        except ValueError:
            await interaction.response.send_message("Неверный формат тега принимающего. Укажите @username.", ephemeral=True)
            return

        embed = discord.Embed(title="Принятие", color=discord.Color.green())
        embed.add_field(name="Принимаемый:", value=f"{self.accepted_tag.value}\n**Ник:** {accepted_nickname}", inline=True)
        embed.add_field(name="Принимающий:", value=f"{self.acceptor_tag.value}\n**Ник:** {acceptor_nickname}", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=False)

# Модальное окно для команды /повышение
class PromotionModal(Modal, title="Повышение"):
    promoted_tag = TextInput(label="Тег повышаемого (@user)", placeholder="@username")
    promoter_tag = TextInput(label="Тег повышающего (@user)", placeholder="@username")
    from_rank = TextInput(label="С какого ранга", placeholder="Название роли")
    to_rank = TextInput(label="На какой ранг", placeholder="Название роли")
    reason = TextInput(label="Причина повышения", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            promoted_id = int(self.promoted_tag.value.replace("<@", "").replace(">", ""))
            promoted_member = interaction.guild.get_member(promoted_id)
            if not promoted_member:
                await interaction.response.send_message("Участник (повышаемый) не найден на сервере.", ephemeral=True)
                return
            promoted_nickname = promoted_member.display_name
        except ValueError:
            await interaction.response.send_message("Неверный формат тега повышаемого. Укажите @username.", ephemeral=True)
            return

        try:
            promoter_id = int(self.promoter_tag.value.replace("<@", "").replace(">", ""))
            promoter_member = interaction.guild.get_member(promoter_id)
            if not promoter_member:
                await interaction.response.send_message("Участник (повышающий) не найден на сервере.", ephemeral=True)
                return
            promoter_nickname = promoter_member.display_name
        except ValueError:
            await interaction.response.send_message("Неверный формат тега повышающего. Укажите @username.", ephemeral=True)
            return

        # Поиск ролей на сервере
        from_role = discord.utils.get(interaction.guild.roles, name=self.from_rank.value)
        to_role = discord.utils.get(interaction.guild.roles, name=self.to_rank.value)

        if not from_role:
            await interaction.response.send_message(f"Роль '{self.from_rank.value}' не найдена на сервере.", ephemeral=True)
            return
        if not to_role:
            await interaction.response.send_message(f"Роль '{self.to_rank.value}' не найдена на сервере.", ephemeral=True)
            return

        # Изменение ролей
        try:
            if from_role in promoted_member.roles:
                await promoted_member.remove_roles(from_role)
            await promoted_member.add_roles(to_role)
        except discord.Forbidden:
            await interaction.response.send_message("У бота недостаточно прав для управления ролями.", ephemeral=True)
            return

        embed = discord.Embed(title="Повышение", color=discord.Color.blue())
        embed.add_field(name="Повышаемый:", value=f"{self.promoted_tag.value}\n**Ник:** {promoted_nickname}", inline=True)
        embed.add_field(name="Повышающий:", value=f"{self.promoter_tag.value}\n**Ник:** {promoter_nickname}", inline=True)
        embed.add_field(name="С какого ранга:", value=self.from_rank.value, inline=False)
        embed.add_field(name="На какой ранг:", value=self.to_rank.value, inline=False)
        embed.add_field(name="Причина:", value=self.reason.value, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=False)

# Модальное окно для команды /понижение
class DemotionModal(Modal, title="Понижение"):
    demoted_tag = TextInput(label="Тег понижаемого (@user)", placeholder="@username")
    demoter_tag = TextInput(label="Тег понижающего (@user)", placeholder="@username")
    from_rank = TextInput(label="С какого ранга", placeholder="Название роли")
    to_rank = TextInput(label="На какой ранг", placeholder="Название роли")
    reason = TextInput(label="Причина понижения", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            demoted_id = int(self.demoted_tag.value.replace("<@", "").replace(">", ""))
            demoted_member = interaction.guild.get_member(demoted_id)
            if not demoted_member:
                await interaction.response.send_message("Участник (понижаемый) не найден на сервере.", ephemeral=True)
                return
            demoted_nickname = demoted_member.display_name
        except ValueError:
            await interaction.response.send_message("Неверный формат тега понижаемого. Укажите @username.", ephemeral=True)
            return

        try:
            demoter_id = int(self.demoter_tag.value.replace("<@", "").replace(">", ""))
            demoter_member = interaction.guild.get_member(demoter_id)
            if not demoter_member:
                await interaction.response.send_message("Участник (понижающий) не найден на сервере.", ephemeral=True)
                return
            demoter_nickname = demoter_member.display_name
        except ValueError:
            await interaction.response.send_message("Неверный формат тега понижающего. Укажите @username.", ephemeral=True)
            return

        # Поиск ролей на сервере
        from_role = discord.utils.get(interaction.guild.roles, name=self.from_rank.value)
        to_role = discord.utils.get(interaction.guild.roles, name=self.to_rank.value)

        if not from_role:
            await interaction.response.send_message(f"Роль '{self.from_rank.value}' не найдена на сервере.", ephemeral=True)
            return
        if not to_role:
            await interaction.response.send_message(f"Роль '{self.to_rank.value}' не найдена на сервере.", ephemeral=True)
            return

        # Изменение ролей
        try:
            if from_role in demoted_member.roles:
                await demoted_member.remove_roles(from_role)
            await demoted_member.add_roles(to_role)
        except discord.Forbidden:
            await interaction.response.send_message("У бота недостаточно прав для управления ролями.", ephemeral=True)
            return

        embed = discord.Embed(title="Понижение", color=discord.Color.orange())
        embed.add_field(name="Понижаемый:", value=f"{self.demoted_tag.value}\n**Ник:** {demoted_nickname}", inline=True)
        embed.add_field(name="Понижающий:", value=f"{self.demoter_tag.value}\n**Ник:** {demoter_nickname}", inline=True)
        embed.add_field(name="С какого ранга:", value=self.from_rank.value, inline=False)
        embed.add_field(name="На какой ранг:", value=self.to_rank.value, inline=False)
        embed.add_field(name="Причина:", value=self.reason.value, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=False)

# Модальное окно для команды /отстранение
class SuspensionModal(Modal, title="Отстранение"):
    suspended_tag = TextInput(label="Тег отстраняемого (@user)", placeholder="@username")
    suspender_tag = TextInput(label="Тег отстраняющего (@user)", placeholder="@username")
    reason = TextInput(label="Причина отстранения", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            suspended_id = int(self.suspended_tag.value.replace("<@", "").replace(">", ""))
            suspended_member = interaction.guild.get_member(suspended_id)
            if not suspended_member:
                await interaction.response.send_message("Участник (отстраняемый) не найден на сервере.", ephemeral=True)
                return
            suspended_nickname = suspended_member.display_name
        except ValueError:
            await interaction.response.send_message("Неверный формат тега отстраняемого. Укажите @username.", ephemeral=True)
            return

        try:
            suspender_id = int(self.suspender_tag.value.replace("<@", "").replace(">", ""))
            suspender_member = interaction.guild.get_member(suspender_id)
            if not suspender_member:
                await interaction.response.send_message("Участник (отстраняющий) не найден на сервере.", ephemeral=True)
                return
            suspender_nickname = suspender_member.display_name
        except ValueError:
            await interaction.response.send_message("Неверный формат тега отстраняющего. Укажите @username.", ephemeral=True)
            return

        embed = discord.Embed(title="Отстранение", color=discord.Color.purple())
        embed.add_field(name="Отстраняемый:", value=f"{self.suspended_tag.value}\n**Ник:** {suspended_nickname}", inline=True)
        embed.add_field(name="Отстраняющий:", value=f"{self.suspender_tag.value}\n**Ник:** {suspender_nickname}", inline=True)
        embed.add_field(name="Причина:", value=self.reason.value, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=False)

# Регистрация команд
@tree.command(name="увольнение", description="Уволить участника")
async def dismissal(interaction: discord.Interaction):
    await interaction.response.send_modal(DismissalModal())

@tree.command(name="принятие", description="Принять участника")
async def acceptance(interaction: discord.Interaction):
    await interaction.response.send_modal(AcceptanceModal())

@tree.command(name="повышение", description="Повысить участника")
async def promotion(interaction: discord.Interaction):
    await interaction.response.send_modal(PromotionModal())

@tree.command(name="понижение", description="Понизить участника")
async def demotion(interaction: discord.Interaction):
    await interaction.response.send_modal(DemotionModal())

@tree.command(name="отстранение", description="Отстранить участника")
async def suspension(interaction: discord.Interaction):
    await interaction.response.send_modal(SuspensionModal())

# Событие готовности бота
@client.event
async def on_ready():
    print(f"Бот {client.user} готов!")
    await tree.sync()  # Синхронизация слэш-команд

# Запуск бота
async def main():
    async with client:
        client.run("MTM5MDAzMzc4Nzc2MDY3NzA0NQ.GTfxw1.s3RLF30NJS1q2LZP5Kb8HViNM5lo5-15qqwdiA")  # Замените на токен вашего бота

if __name__ == "__main__":
    asyncio.run(main())
