const { runIntegration } = require('./index');
const config = require('./config');

/**
 * Run the integration on a schedule
 * Polls Kajabi every X minutes for new sales
 */
async function startScheduler() {
  console.log(`Scheduler started. Will check for new sales every ${config.pollInterval} minutes.\n`);

  // Run immediately on start
  await runIntegration();

  // Then run on interval
  setInterval(async () => {
    console.log('\n--- Scheduled run ---');
    await runIntegration();
  }, config.pollInterval * 60 * 1000);
}

startScheduler().catch(error => {
  console.error('Scheduler error:', error);
  process.exit(1);
});
