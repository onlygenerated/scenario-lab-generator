export type Topic = {
  id: string;
  name: string;
  description: string;
  available: boolean;
};

export type Category = {
  id: string;
  name: string;
  icon: string;
  description: string;
  topics: Topic[];
};

export const CATEGORIES: Category[] = [
  {
    id: 'data-engineering',
    name: 'Data Engineering',
    icon: '🔧',
    description: 'Build and maintain the pipelines that move data from source to destination.',
    topics: [
      {
        id: 'etl-pipelines',
        name: 'ETL Pipelines',
        description: 'Extract, transform, and load data between systems using SQL and Python.',
        available: true,
      },
      {
        id: 'data-modeling',
        name: 'Data Modeling',
        description: 'Design schemas, normalize tables, and define relationships.',
        available: true,
      },
      {
        id: 'data-quality',
        name: 'Data Quality',
        description: 'Validate, clean, and monitor data for correctness and completeness.',
        available: false,
      },
    ],
  },
  {
    id: 'data-science',
    name: 'Data Science',
    icon: '📊',
    description: 'Analyze datasets, engineer features, and test hypotheses.',
    topics: [
      {
        id: 'exploratory-analysis',
        name: 'Exploratory Analysis',
        description: 'Investigate datasets to discover patterns, outliers, and insights.',
        available: false,
      },
      {
        id: 'feature-engineering',
        name: 'Feature Engineering',
        description: 'Create and select features that improve model performance.',
        available: false,
      },
      {
        id: 'statistical-testing',
        name: 'Statistical Testing',
        description: 'Apply hypothesis tests and confidence intervals to draw conclusions.',
        available: false,
      },
    ],
  },
  {
    id: 'devops',
    name: 'DevOps',
    icon: '🚀',
    description: 'Automate deployments, manage containers, and provision infrastructure.',
    topics: [
      {
        id: 'cicd-pipelines',
        name: 'CI/CD Pipelines',
        description: 'Build continuous integration and delivery workflows.',
        available: false,
      },
      {
        id: 'container-orchestration',
        name: 'Container Orchestration',
        description: 'Deploy and manage multi-container applications.',
        available: false,
      },
      {
        id: 'infrastructure-as-code',
        name: 'Infrastructure as Code',
        description: 'Provision and configure infrastructure declaratively.',
        available: false,
      },
    ],
  },
  {
    id: 'networking',
    name: 'Networking',
    icon: '🌐',
    description: 'Configure network services, routing, and traffic management.',
    topics: [
      {
        id: 'routing-switching',
        name: 'Routing & Switching',
        description: 'Configure routers, switches, VLANs, and routing protocols.',
        available: false,
      },
      {
        id: 'firewall-rules',
        name: 'Firewall Rules',
        description: 'Define and manage network security policies and ACLs.',
        available: false,
      },
      {
        id: 'dns-load-balancing',
        name: 'DNS & Load Balancing',
        description: 'Set up DNS resolution and distribute traffic across servers.',
        available: false,
      },
    ],
  },
  {
    id: 'security',
    name: 'Security',
    icon: '🔒',
    description: 'Assess vulnerabilities, manage access, and respond to incidents.',
    topics: [
      {
        id: 'vulnerability-assessment',
        name: 'Vulnerability Assessment',
        description: 'Scan and evaluate systems for security weaknesses.',
        available: false,
      },
      {
        id: 'access-control',
        name: 'Access Control',
        description: 'Implement authentication, authorization, and permission models.',
        available: false,
      },
      {
        id: 'incident-response',
        name: 'Incident Response',
        description: 'Detect, investigate, and remediate security incidents.',
        available: false,
      },
    ],
  },
];
