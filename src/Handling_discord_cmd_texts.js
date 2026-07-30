import { ActionRowBuilder, ButtonBuilder, ButtonStyle, EmbedBuilder } from "discord.js";
import { DateTime } from "luxon";
import glob from "./glob.js";
import T from "./T.js";

export default class Handling_discord_cmd_texts {

    static processCommand = async (client, message) => {
        
        T.lgreen(`Processing command: ${message.content}`);
        T.lgreen(`from ${message?.nickname ?? message?.displayName ?? message?.author?.username}`);

        // remove the '!!' prefix
        const commandBody = message.content.slice(2).trim();

        // check the first word as command
        const args = commandBody.split(' ');
        const command = args.shift().toLowerCase();

        switch (command) {
            case 'leave-server':
                if (message.channel.type === 'DM') leaveServer(client, args[0]); else message.reply(`You must use this command in a DM.`);
                break;
            case 'list-servers':
                logAllServers(message);
                break;
            case 'ping':
                ping(client, message);
                break;
            case 'demo': {
                let state = dailyStates.get(message.author.id);
                if (!state) {
                    state = { yesterday: DEFAULT_YESTERDAY, today: DEFAULT_TODAY };
                    dailyStates.set(message.author.id, state);
                }
                await sendDailyEmbed(message, state);
                break;
            }
            case 'edit_yesterday': {
                let state = dailyStates.get(message.author.id);
                if (!state) {
                    state = { yesterday: DEFAULT_YESTERDAY, today: DEFAULT_TODAY };
                }
                const newText = args.join(' ').trim();
                if (newText) {
                    state.yesterday = newText;
                }
                dailyStates.set(message.author.id, state);
                await sendDailyEmbed(message, state);
                break;
            }
            case 'edit_today': {
                let state = dailyStates.get(message.author.id);
                if (!state) {
                    state = { yesterday: DEFAULT_YESTERDAY, today: DEFAULT_TODAY };
                }
                const newText = args.join(' ').trim();
                if (newText) {
                    state.today = newText;
                }
                dailyStates.set(message.author.id, state);
                await sendDailyEmbed(message, state);
                break;
            }
        }
    }


}





const ping = async (client, message) => {
    await message.reply('Pong!');
}










const leaveServer = async (client, server_id) => {
    try {
        // Fetch the guild if it's not in cache
        const guild = await client.guilds.fetch(server_id);
        
        if (!guild) {
            console.log(`Guild with ID ${server_id} not found`);
            return false;
        }
        
        await guild.leave();
        T.lBrightGreen(`Successfully left server: ${guild.name} (${server_id})`);
        logAllServers();
        return true;
        
    } catch (error) {
        console.error(`Error leaving server ${server_id}:`, error);
        return false;
    }
};


const dailyStates = new Map();
const DEFAULT_YESTERDAY = "Hoàn thành Slide Presentation chuẩn bị cho buổi Mentor Review.";
const DEFAULT_TODAY = "Cập nhật UI Figma cho màn hình Register (thêm trường Số điện thoại). [Link Figma]";

const sendDailyEmbed = async (message, state) => {
    const displayName = message?.member?.nickname ?? message?.member?.displayName ?? message?.author?.globalName ?? message?.author?.username;
    const embed = new EmbedBuilder()
        .setColor('#00d2ff')
        .setTitle('Báo cáo Daily')
        .setDescription(`Xin chào **${displayName}**!\nĐã đến lúc nộp daily, hãy để tôi giúp bạn:`)
        .addFields(
            { name: 'Công việc đã làm hôm qua', value: state.yesterday },
            { name: 'Công việc sẽ làm hôm nay', value: state.today },
            { name: 'Copy lệnh', value: 'Nếu thấy nội dung này ok, hãy bấm nút copy lệnh daily' }
        );

    const copyButton = new ButtonBuilder()
        .setCustomId('copy_daily')
        .setLabel('Copy Lệnh Daily')
        .setStyle(ButtonStyle.Primary);

    const editYesterdayBtn = new ButtonBuilder()
        .setCustomId('edit_yesterday_btn')
        .setLabel('Edit Yesterday')
        .setStyle(ButtonStyle.Secondary);

    const editTodayBtn = new ButtonBuilder()
        .setCustomId('edit_today_btn')
        .setLabel('Edit Today')
        .setStyle(ButtonStyle.Secondary);

    const row = new ActionRowBuilder().addComponents(copyButton, editYesterdayBtn, editTodayBtn);

    const response = await message.reply({
        embeds: [embed],
        components: [row]
    });

    const collectorFilter = i => i.user.id === message.author.id;
    try {
        const confirmation = await response.awaitMessageComponent({ filter: collectorFilter, time: 60_000 });
        if (confirmation.customId === 'copy_daily') {
            await confirmation.update({ components: [] });
            await message.channel.send(`/daily yesterday:${state.yesterday} today:${state.today}`);
        } else if (confirmation.customId === 'edit_yesterday_btn') {
            await confirmation.update({ components: [] });
            await message.channel.send(`!!edit_yesterday ${state.yesterday}`);
        } else if (confirmation.customId === 'edit_today_btn') {
            await confirmation.update({ components: [] });
            await message.channel.send(`!!edit_today ${state.today}`);
        }
    } catch (e) {
        // ignore timeout
    }
};










/**
 * 
 * @_param {import('discord.js').Client} client
 * @param {import('discord.js').Message} [message]
 * @returns 
 */
export const logAllServers = (message) => {

    let str = `Bot is currently in ${glob.CLIENT.guilds.cache.size} server(s):\n`;
    
    let idx = 0;
    glob.CLIENT.guilds.cache.forEach((guild, _) => {
        if (!guild) {
            str += "\n" + (`${idx + 1}. Server: Unknown`);
            str += "\n" + ('-'.repeat(40));
        }
        else {
            str += "\n" + (`${idx + 1}. Server: ${guild.name}`);
            str += "\n" + (`   ID: ${guild.id}`);
            str += "\n" + (`   Members: ${guild.memberCount}`);
            str += "\n" + (`   Owner: ${guild.ownerId}`);
            str += "\n" + (`   Created: ${guild.createdAt.toDateString()}`);
            str += "\n" + (`   Bot joined: ${guild.joinedAt ? guild.joinedAt.toDateString() : 'Unknown'}`);
            str += "\n" + ('-'.repeat(40));
        }
    });
    
    let result = (`\nTotal servers: ${glob.CLIENT.guilds.cache.size}`);
    T.lgreen(result);

    if (!!message)
        message.reply(str + "\n" + result).catch(err => {
            T.lred(`Failed to send message in channel ${message.channel.id}: ${err}`);
        });

    return result + "\n" + str;
}