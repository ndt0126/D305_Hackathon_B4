import { BaseInteraction, ChatInputCommandInteraction, Client, CommandInteraction, CommandInteractionOptionResolver, REST, Routes, SlashCommandBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, EmbedBuilder } from "discord.js";
import config from "./config.js";
import { DateTime } from "luxon";
import fs from "fs/promises";


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
            ,
            new SlashCommandBuilder()
                .setName('demo_scan_this').setDescription('Scan chat history of the current channel and save to disk')
            ,
            new SlashCommandBuilder()
                .setName('register_llm_endpoint').setDescription('Register an LLM endpoint URL')
                .addStringOption(option =>
                    option.setName('url').setDescription('The LLM endpoint URL').setRequired(true)
                )
            ,
            new SlashCommandBuilder()
                .setName('register_llm_endpoint_2').setDescription('Register the second LLM endpoint URL')
                .addStringOption(option =>
                    option.setName('url').setDescription('The second LLM endpoint URL').setRequired(true)
                )
            ,
            new SlashCommandBuilder()
                .setName('demo2').setDescription('POST chat history JSON to the registered LLM endpoint')
                .addBooleanOption(option =>
                    option.setName('force_refresh').setDescription('Force refresh LLM response bypassing cache').setRequired(false)
                )
            ,
            new SlashCommandBuilder()
                .setName('weekly')
                .setDescription('Weekly command')
                .addSubcommand(subcommand =>
                    subcommand
                        .setName('submit')
                        .setDescription('Submit weekly report')
                        .addStringOption(option => option.setName('done').setDescription('Done tasks').setRequired(true))
                        .addStringOption(option => option.setName('doing').setDescription('Doing tasks').setRequired(true))
                        .addStringOption(option => option.setName('blocked').setDescription('Blocked issues').setRequired(true))
                        .addStringOption(option => option.setName('questions').setDescription('Questions or suggestions').setRequired(true))
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
        const { commandName } = interaction;
        if (commandName === 'demo_scan_this') {
            await interaction.deferReply({ ephemeral: true });
        } else {
            await interaction.deferReply(); // Acknowledge the interaction
        }
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
                case 'demo_scan_this': {
                    try {
                        await interaction.editReply("Scanning chat history...");
                        const channel = interaction.channel;
                        let allMessages = [];
                        let lastId = null;
                        while (true) {
                            const options = { limit: 100 };
                            if (lastId) {
                                options.before = lastId;
                            }
                            const messages = await channel.messages.fetch(options);
                            if (messages.size === 0) {
                                break;
                            }
                            allMessages.push(...messages.values());
                            lastId = messages.lastKey();
                            
                            // Update progress only to the user who ran the command
                            await interaction.editReply(`Scanning chat history... (Fetched ${allMessages.length} messages)`);

                            if (messages.size < 100) {
                                break;
                            }
                        }
                        
                        const formattedHistory = await Promise.all(allMessages.map(async msg => {
                            let content = msg.content || "";
                            for (const att of msg.attachments.values()) {
                                const urlPath = att.url.split('?')[0];
                                if (urlPath.endsWith('.txt') || urlPath.endsWith('.md')) {
                                    try {
                                        const fileResponse = await fetch(att.url);
                                        if (fileResponse.ok) {
                                            const fileContent = await fileResponse.text();
                                            content += `\n[Attached File Content (${att.name || 'file'}):\n${fileContent}\n]`;
                                        }
                                    } catch (fetchErr) {
                                        console.error(`Failed to fetch attachment content from ${att.url}:`, fetchErr);
                                    }
                                }
                            }
                            return {
                                id: msg.id,
                                guild_id: msg.guildId,
                                channel_id: msg.channelId,
                                message_id: msg.id,
                                author: msg.member?.nickname ?? msg.member?.displayName ?? msg.author.displayName ?? msg.author.globalName ?? msg.author.username,
                                author_discord_id: msg.author.id,
                                content: content,
                                attached_file_urls: msg.attachments.map(att => att.url),
                                timestamp: msg.createdAt
                            };
                        }));

                        await fs.mkdir("./run_data", { recursive: true });
                        await fs.writeFile("./run_data/chat_history.json", JSON.stringify(formattedHistory, null, 2), "utf8");
                        await interaction.editReply(`Scan complete! Saved ${formattedHistory.length} messages to disk.`);
                    } catch (error) {
                        console.error("Error scanning chat history:", error);
                        await interaction.editReply("Failed to scan chat history.");
                    }
                    break;
                }
                case 'register_llm_endpoint': {
                    try {
                        const url = interaction.options.getString('url');
                        await fs.mkdir("./run_data", { recursive: true });
                        await fs.writeFile("./run_data/llm_endpoint.txt", url, "utf8");
                        await interaction.editReply(`Successfully registered LLM endpoint: ${url}`);
                    } catch (error) {
                        console.error("Error registering LLM endpoint:", error);
                        await interaction.editReply("Failed to register LLM endpoint.");
                    }
                    break;
                }
                case 'register_llm_endpoint_2': {
                    try {
                        const url = interaction.options.getString('url');
                        await fs.mkdir("./run_data", { recursive: true });
                        await fs.writeFile("./run_data/llm_endpoint_2.txt", url, "utf8");
                        await interaction.editReply(`Successfully registered LLM endpoint 2: ${url}`);
                    } catch (error) {
                        console.error("Error registering LLM endpoint 2:", error);
                        await interaction.editReply("Failed to register LLM endpoint 2.");
                    }
                    break;
                }
                case 'demo2': {
                    try {
                        const force_refresh = interaction.options.getBoolean('force_refresh') || false;
                        let data = null;
                        const todayStr = DateTime.now().toFormat('yyyy-MM-dd');
                        
                        if (!force_refresh) {
                            try {
                                const cacheRaw = await fs.readFile("./run_data/llm_cached_response.json", "utf8");
                                const cacheParsed = JSON.parse(cacheRaw);
                                if (cacheParsed.date === todayStr) {
                                    data = cacheParsed.response;
                                    console.log("[demo2] Using cached LLM response for today:", todayStr);
                                    await interaction.editReply("Using cached LLM response for today...");
                                }
                            } catch (e) {
                                console.log("[demo2] No valid cache found or cache date mismatch. Fetching fresh response...");
                            }
                        }

                        if (!data) {
                            let endpoint;
                            try {
                                endpoint = (await fs.readFile("./run_data/llm_endpoint.txt", "utf8")).trim();
                            } catch (e) {
                                await interaction.editReply("No LLM endpoint registered yet. Please use /register_llm_endpoint first.");
                                break;
                            }
                            
                            let chatHistory;
                            try {
                                chatHistory = await fs.readFile("./run_data/chat_history.json", "utf8");
                            } catch (e) {
                                await interaction.editReply("No chat history file found. Please use /demo_scan_this first.");
                                break;
                            }

                            await interaction.editReply(`Sending chat history to LLM...`);
                            const response = await fetch(endpoint, {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json",
                                    "X-API-Key": "GknEzH1oU8uGUlKY9DOZpUhzYiHiEeCAYbmvE14TYhc"
                                },
                                body: chatHistory
                            });

                            const responseText = await response.text();
                            console.log("[demo2] POST response received. Length:", responseText.length);
                            console.log("[demo2] Raw response text:", responseText);
                            
                            try {
                                data = JSON.parse(responseText);
                                console.log("[demo2] JSON parsed successfully:", JSON.stringify(data, null, 2));
                                
                                const cacheData = {
                                    date: todayStr,
                                    response: data
                                };
                                await fs.mkdir("./run_data", { recursive: true });
                                await fs.writeFile("./run_data/llm_cached_response.json", JSON.stringify(cacheData, null, 2), "utf8");
                            } catch (e) {
                                console.error("[demo2] Failed to parse JSON:", e);
                                await interaction.editReply(`Response from LLM:\n${responseText.substring(0, 1900)}`);
                                break;
                            }
                        }

                        await interaction.editReply("Processing LLM response...");
                        
                        // 1. Process dailies
                        if (data.dailies && Array.isArray(data.dailies)) {
                            console.log("[demo2] Found dailies array. Length:", data.dailies.length);
                            
                            for (const item of data.dailies) {
                                const target_username = item.target_username || item.target_discord_id;
                                console.log(`[demo2] Processing daily item for username/id: "${target_username}"`, item);
                                
                                if (item.target_discord_id === client.user.id) {
                                    console.log(`[demo2] Skipping item because target_discord_id is the bot itself: ${item.target_discord_id}`);
                                    continue;
                                }

                                let member = null;
                                if (item.target_discord_id) {
                                    console.log(`[demo2] Attempting to fetch member directly by ID: ${item.target_discord_id}`);
                                    member = await interaction.guild.members.fetch(item.target_discord_id).catch((err) => {
                                        console.error(`[demo2] Error fetching member with target_discord_id "${item.target_discord_id}":`, err);
                                        return null;
                                    });
                                }
                                if (!member && item.target_username) {
                                    console.log(`[demo2] Attempting to find member in cache by username: ${item.target_username}`);
                                    member = interaction.guild.members.cache.find(m => 
                                        m.nickname?.toLowerCase() === item.target_username.toLowerCase() || 
                                        m.displayName?.toLowerCase() === item.target_username.toLowerCase() || 
                                        m.user.username.toLowerCase() === item.target_username.toLowerCase()
                                    );
                                }

                                console.log(`[demo2] Resolved member:`, member ? `${member.user.tag} (ID: ${member.id})` : "NOT FOUND");

                                const displayName = member ? (member.nickname ?? member.displayName) : target_username;
                                const embed = new EmbedBuilder()
                                    .setColor('#00d2ff')
                                    .setTitle('Báo cáo Daily')
                                    .setDescription(`Xin chào **${displayName}**!\nĐã đến lúc nộp daily, hãy để tôi giúp bạn:`)
                                    .addFields(
                                        { name: 'Công việc đã làm hôm qua', value: item.yesterday || 'None' },
                                        { name: 'Công việc sẽ làm hôm nay', value: item.today || 'None' },
                                        { name: 'Nếu thấy nội dung này ok, hãy copy lệnh dưới đây', value: `\`/daily yesterday:${item.yesterday} today:${item.today}\`` }
                                    );

                                const editYesterdayBtn = new ButtonBuilder()
                                    .setCustomId(`edit_yesterday_btn_${target_username}`)
                                    .setLabel('Edit Yesterday')
                                    .setStyle(ButtonStyle.Secondary);

                                const editTodayBtn = new ButtonBuilder()
                                    .setCustomId(`edit_today_btn_${target_username}`)
                                    .setLabel('Edit Today')
                                    .setStyle(ButtonStyle.Secondary);

                                const row = new ActionRowBuilder().addComponents(editYesterdayBtn, editTodayBtn);

                                if (member) {
                                    try {
                                        console.log(`[demo2] Attempting to send DM to ${member.user.tag}...`);
                                        const dmChannel = await member.createDM();
                                        const responseMsg = await dmChannel.send({ embeds: [embed], components: [row] });
                                        console.log(`[demo2] DM sent successfully to ${member.user.tag}`);
                                        const collector = responseMsg.createMessageComponentCollector({ time: 60000 });
                                        collector.on('collect', async i => {
                                            if (i.customId.startsWith('edit_yesterday_btn_')) {
                                                await i.update({ components: [] });
                                                await dmChannel.send(`!!edit_yesterday ${item.yesterday}`);
                                            } else if (i.customId.startsWith('edit_today_btn_')) {
                                                await i.update({ components: [] });
                                                await dmChannel.send(`!!edit_today ${item.today}`);
                                            }
                                        });
                                    } catch (err) {
                                        console.warn(`[demo2] Failed to send DM to ${member.user.tag}. Falling back to channel...`, err);
                                        const channelResponse = await interaction.channel.send({ content: `<@${member.id}>`, embeds: [embed], components: [row] });
                                        const collector = channelResponse.createMessageComponentCollector({ time: 60000 });
                                        collector.on('collect', async i => {
                                            if (i.user.id === member.id) {
                                                if (i.customId.startsWith('edit_yesterday_btn_')) {
                                                    await i.update({ components: [] });
                                                    await interaction.channel.send(`!!edit_yesterday ${item.yesterday}`);
                                                } else if (i.customId.startsWith('edit_today_btn_')) {
                                                    await i.update({ components: [] });
                                                    await interaction.channel.send(`!!edit_today ${item.today}`);
                                                }
                                            }
                                        });
                                    }
                                } else {
                                    console.warn(`[demo2] User "${target_username}" not found. Sending to admin user ${config.MY_DISCORD_ACCOUNT_ID}...`);
                                    try {
                                        const adminUser = await client.users.fetch(config.MY_DISCORD_ACCOUNT_ID);
                                        if (adminUser) {
                                            const dmChannel = await adminUser.createDM();
                                            const responseMsg = await dmChannel.send({ content: `Không tìm thấy user **${target_username}** trong server này.`, embeds: [embed], components: [row] });
                                            const collector = responseMsg.createMessageComponentCollector({ time: 60000 });
                                            collector.on('collect', async i => {
                                                if (i.customId.startsWith('edit_yesterday_btn_')) {
                                                    await i.update({ components: [] });
                                                    await dmChannel.send(`!!edit_yesterday ${item.yesterday}`);
                                                } else if (i.customId.startsWith('edit_today_btn_')) {
                                                    await i.update({ components: [] });
                                                    await dmChannel.send(`!!edit_today ${item.today}`);
                                                }
                                            });
                                        }
                                    } catch (adminErr) {
                                        console.error(`[demo2] Failed to send message to admin:`, adminErr);
                                    }
                                }
                            }
                        } else {
                            console.log("[demo2] No dailies array found in response.");
                        }

                        // 2. Process weekly
                        if (data.weekly) {
                            console.log("[demo2] Found weekly data:", data.weekly);
                            const weekly = data.weekly;
                            const weeklyEmbed = new EmbedBuilder()
                                .setColor('#ff9900')
                                // .setTitle('Báo cáo Weekly')
                                .setTitle('Tình hình chung')
                                .setDescription('Trạng thái của nhóm:')
                                .addFields(
                                    { name: 'Done', value: weekly.done || 'None' },
                                    { name: 'Doing', value: weekly.doing || 'None' },
                                    { name: 'Blocked', value: weekly.blocked || 'None' },
                                    { name: 'Questions', value: weekly.questions || 'None' },
                                    { name: 'Nếu thấy nội dung này ok, hãy copy lệnh dưới đây', value: `\`/weekly submit done:${weekly.done.replace("\n- ", ", ")} doing:${weekly.doing.replace("\n- ", ", ")} blocked:${weekly.blocked.replace("\n- ", ", ")} questions:${weekly.questions.replace("\n- ", ", ")}\`` }
                                );

                            // const editDoneBtn = new ButtonBuilder()
                            //     .setCustomId('edit_done_btn')
                            //     .setLabel('Edit Done')
                            //     .setStyle(ButtonStyle.Secondary);

                            // const editDoingBtn = new ButtonBuilder()
                            //     .setCustomId('edit_doing_btn')
                            //     .setLabel('Edit Doing')
                            //     .setStyle(ButtonStyle.Secondary);

                            // const editBlockedBtn = new ButtonBuilder()
                            //     .setCustomId('edit_blocked_btn')
                            //     .setLabel('Edit Blocked')
                            //     .setStyle(ButtonStyle.Secondary);

                            // const editQuestionsBtn = new ButtonBuilder()
                            //     .setCustomId('edit_questions_btn')
                            //     .setLabel('Edit Questions')
                            //     .setStyle(ButtonStyle.Secondary);

                            // const row = new ActionRowBuilder().addComponents(editDoneBtn, editDoingBtn, editBlockedBtn);
                            // const row2 = new ActionRowBuilder().addComponents(editQuestionsBtn);
                            // const weeklyResponse = await interaction.channel.send({ embeds: [weeklyEmbed], components: [row, row2] });
                            const weeklyResponse = await interaction.channel.send({ embeds: [weeklyEmbed] });


                            console.log("[demo2] Weekly report embed sent to channel.");
                            const weeklyCollector = weeklyResponse.createMessageComponentCollector({ time: 60000 });
                            weeklyCollector.on('collect', async i => {
                                if (i.customId === 'edit_done_btn') {
                                    await i.update({ components: [] });
                                    await interaction.channel.send(`!!edit_done ${weekly.done}`);
                                } else if (i.customId === 'edit_doing_btn') {
                                    await i.update({ components: [] });
                                    await interaction.channel.send(`!!edit_doing ${weekly.doing}`);
                                } else if (i.customId === 'edit_blocked_btn') {
                                    await i.update({ components: [] });
                                    await interaction.channel.send(`!!edit_blocked ${weekly.blocked}`);
                                } else if (i.customId === 'edit_questions_btn') {
                                    await i.update({ components: [] });
                                    await interaction.channel.send(`!!edit_questions ${weekly.questions}`);
                                }
                            });
                        } else {
                            console.log("[demo2] No weekly data found in response.");
                        }

                        await interaction.editReply("LLM response processed successfully!");
                    } catch (error) {
                        console.error("Error in demo2 command:", error);
                        await interaction.editReply("Failed to send chat history to LLM endpoint.");
                    }
                    break;
                }
                case 'weekly': {
                    try {
                        const subcommand = interaction.options.getSubcommand();
                        if (subcommand === 'submit') {
                            const done = interaction.options.getString('done');
                            const doing = interaction.options.getString('doing');
                            const blocked = interaction.options.getString('blocked');
                            const questions = interaction.options.getString('questions');
                            await interaction.editReply(`Weekly report submitted successfully!\n- **Done**: ${done}\n- **Doing**: ${doing}\n- **Blocked**: ${blocked}\n- **Questions**: ${questions}`);
                        }
                    } catch (error) {
                        console.error("Error submitting weekly report:", error);
                        await interaction.editReply("Failed to submit weekly report.");
                    }
                    break;
                }
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
