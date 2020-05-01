class AuditFeatures {
    constructor({repositories}) {
        this.auditRepo = repositories.AuditRepository;
    }

   async getAuditsForDevice({accountId,deviceId, sort, limit, skip, from, to}) {
        const result = await this.auditRepo.getAuditForDevice({accountId, deviceId, from, to, sort, skip, limit});
        return result;
    }
}

module.exports = AuditFeatures;