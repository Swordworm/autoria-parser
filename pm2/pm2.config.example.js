const path = require('path');
const {
    PYTHON_INTERPRETER,
    SCRAPY_SCRIPT,
    PROJECT_PREFIX,
    MAX_MEMORY_RESTART,
    PYTHON_CWD,
    PM2_LOG_DIRECTORY,
} = require('./settings/settings');

const spiders = [
    {
        name: `${PROJECT_PREFIX}_serp_spider`,
        script: SCRAPY_SCRIPT,
        args: "crawl autoria_serp_spider",
        interpreter: PYTHON_INTERPRETER,
        instances: 1,
        cron_restart: "0 12 * * *"
    },
];

const commands = [
    {
        name: `${PROJECT_PREFIX}_exporter`,
        script: SCRAPY_SCRIPT,
        args: "exporter",
        interpreter: PYTHON_INTERPRETER,
        instances: 1,
        cron_restart: "0 0 * * *"
    },
];

const processNames = [];
const apps = [];

Array.from([commands, spiders]).map(t => {
    t.reduce((a, v) => {
        if (!v.hasOwnProperty('name') || v.name.length === 0) {
            console.error('ERROR: process name field is required');
            process.exit(1);
        }
        if (processNames.includes(v.name)) {
            console.error(`ERROR: Duplicate process name declared: ${v.name}. Check required`);
            process.exit(1);
        }

        processNames.push(v.name);
        a.push(
            Object.assign(
                {},
                {
                    cwd: PYTHON_CWD,
                    combine_logs: true,
                    merge_logs: true,
                    error_file: path.join(PM2_LOG_DIRECTORY, `${v.name}.log`),
                    out_file: path.join(PM2_LOG_DIRECTORY, `${v.name}.log`),
                    max_restarts: 10,
                    max_memory_restart: MAX_MEMORY_RESTART,
                },
                v,
                (v.hasOwnProperty('cron_restart')) ? {
                    cron_restart: v.cron_restart,
                    autorestart: false,
                } : null,
            )
        );
        return a
    }, apps)
});

module.exports = {
    apps: apps
};
