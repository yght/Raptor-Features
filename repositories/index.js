const AuditRepository = require('./auditRepository');
const DeviceRepository = require('./deviceRepository');
const UsageRepository = require('./usageRepository');
const PlanRepository = require('./planRepository');
const SyncRepository = require('./syncRepository');
const Repositories = ({db}) =>  {
     return {
         AuditRepository: new AuditRepository({db}),
         DeviceRepository: new DeviceRepository({db}),
         UsageRepository: new UsageRepository({db}),
         PlanRepository: new PlanRepository({db}),
         SyncRepository: new SyncRepository({db})
     }
}

module.exports = Repositories;