const AuditFeatures = require('./auditFeatures');
const DeviceFeatures = require('./deviceFeatures');
const UsageFeatures = require('./usageFeatures');
const PlanFeatures = require('./planFeatures');
const SyncFeatures = require('./syncFeatures');


const Features = ({repositories}) =>  {
    return {
        AuditFeatures: new AuditFeatures({repositories}),
        DeviceFeatures: new DeviceFeatures({repositories}),
        UsageFeatures: new UsageFeatures({repositories}),
        PlanFeatures: new PlanFeatures({repositories}),
        SyncFeatures: new SyncFeatures({repositories}),
    }
}

module.exports = Features;