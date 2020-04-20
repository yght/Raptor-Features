class AuditFeatures {
    constructor({repositories}) {
        this.auditRepo = repositories.AuditRepository;
    }

   async getAuditsForICCID(iccid) {
        const result = await this.auditRepo.getAuditForIccid({iccid});
        return result;
    }
}

module.exports = AuditFeatures;