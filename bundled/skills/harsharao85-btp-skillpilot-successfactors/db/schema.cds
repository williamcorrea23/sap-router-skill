namespace skillpilot;

entity Courses {
  key ID           : Integer;
  title            : String(200);
  description      : String(2000);
  duration         : String(50);     // e.g. "8 hours", "3 days"
  format           : String(50);     // e.g. "eLearning", "Instructor-Led", "Blended"
  skillArea        : String(100);    // e.g. "S/4HANA Migration", "BTP", "AI/ML", "Change Management"
  prerequisites    : String(500);
}

entity LearningPaths {
  key ID              : Integer;
  title               : String(200);
  targetRole          : String(100);  // e.g. "Functional Consultant", "Basis Admin", "Change Lead"
  estimatedDuration   : String(50);
  description         : String(2000);
}

entity Certifications {
  key ID            : Integer;
  title             : String(200);
  validityPeriod    : String(50);   // e.g. "2 years"
  renewalRules      : String(500);
  description       : String(1000);
}

entity Skills {
  key ID              : Integer;
  name                : String(100);
  proficiencyLevel    : String(50);   // e.g. "Beginner", "Intermediate", "Advanced"
  description         : String(500);
}
