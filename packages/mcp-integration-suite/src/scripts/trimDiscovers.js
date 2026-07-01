const fs = require("fs");

const resultObj = JSON.parse(
	fs.readFileSync("./resources/Discover/IntegrationPackages.json")
);

resultObj.results = resultObj.results.map((entry) => {
	const unusedAttrs = [
		"__metadata",
		"Licenses",
		"MediaLinks",
		"Urls",
		"Artifacts",
		"reg_id",
		"Featured",
		"Scope",
		"PublishedAt",
		"PublishedBy",
        "CreatedAt",
        "CreatedBy",
        "ModifiedBy",
        "ModifiedAt",
        "PartnerContent",
        "AdditionalAttributes",
        "Files",
        "SubType",
        "Type",
        "CertifiedBySap",
        "CommunityContent",
        "LicenseType",
        "SupportInfo",
        "CommercialContent",
        "AppCenterTechName",
        "PartnerCRMBP",
        "Restricted",
        "Version",
        "OrgName",
        "Vendor",
        "Industries",
        "RatingCount",
        "AvgRating", 
        "Description"
	];
	unusedAttrs.forEach((attr) => delete entry[attr]);

	return entry;
});

fs.writeFileSync(
	"./resources/Discover/IntegrationPackages.json",
	JSON.stringify(resultObj)
);
