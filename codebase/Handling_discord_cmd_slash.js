import { BaseInteraction, ChatInputCommandInteraction, Client, CommandInteraction, CommandInteractionOptionResolver, REST, Routes, SlashCommandBuilder } from "discord.js";
import config from "./config.js";
import Handling_Schwab_bridge from "./Handling_Schwab_bridge.js";
import { DateTime } from "luxon";

export default class Handling_discord_cmd_slash {

    static registerCommands = async () => {

        //MARK: Define SLASH commands 
        const commands = [
            new SlashCommandBuilder()
                .setName('daily').setDescription('Check daily data')
                .addStringOption(option =>
                    option.setName('yesterday').setDescription('Yesterday option').setRequired(false)
                )
                .addStringOption(option =>
                    option.setName('today').setDescription('Today option').setRequired(false)
                )
        ];


        //#region do register 
        const rest = new REST().setToken(config.BOT_TOKEN_A + config.BOT_TOKEN_B + config.BOT_TOKEN_C);

        try {
            console.log('Started refreshing global application (/) commands.');
            // Use Routes.applicationCommands() for global registration
            await rest.put(Routes.applicationCommands('945931546966245426'), { body: commands.map(command => command.toJSON()) },);
            console.log('Successfully reloaded global application (/) commands. Note: Global commands can take up to 1 hour to update across all servers.');
        }
        catch (error) { console.error('Error registering global commands:', error); }
        //#endregion
    }


    /**
     * @param {Client} client 
     * @param {ChatInputCommandInteraction} interaction */
    static processCommand = async (client, interaction) => {
        await interaction.deferReply(); // Acknowledge the interaction
        const { commandName } = interaction;
        try {
            const dateStr = interaction.options.getString('date');
            //MARK: PROCESS COMMANDS 
            switch (commandName) {
                case 'daily':
                    const yesterday = interaction.options.getString('yesterday');
                    const today = interaction.options.getString('today');
                    console.log('daily cmd', yesterday, today);
                    await interaction.editReply(`Daily command received. Yesterday: ${yesterday}, Today: ${today}`);
                    break;
                default:
                    await interaction.editReply('Unknown command!');
            }
        }
        catch (error) {
            console.error(error);
            if (interaction.replied || interaction.deferred) { await interaction.followUp({ content: 'There was an error executing this command!', ephemeral: true }); }
            else { await interaction.reply({ content: 'There was an error executing this command!', ephemeral: true }); }
        }
    }
}
