declare module '@sap/xssec' {
    export interface SecurityContext {
        getUserName(): string;
        getEmail(): string;
        getGivenName(): string;
        getFamilyName(): string;
        getSubdomain(): string;
        getClientId(): string;
        getExpirationDate(): Date;
        getGrantedScopes(): string[];
        checkScope(scope: string): boolean;
        checkLocalScope(scope: string): boolean;
        getToken(): string;
        getHdbToken(): string;
        getAppToken(): string;
        getIdentityZone(): string;
        getSubaccountId(): string;
        isInForeignMode(): boolean;
    }

    export function createSecurityContext(
        token: string,
        xsuaaCredentials: Record<string, unknown>,
        callback: (error: Error | null, securityContext?: SecurityContext) => void
    ): void;

    export function createSecurityContext(
        token: string,
        xsuaaCredentials: Record<string, unknown>
    ): Promise<SecurityContext>;

    export interface XsuaaCredentials {
        url: string;
        clientid: string;
        clientsecret: string;
        identityzone?: string;
        identityzoneid?: string;
        tenantid?: string;
        tenantmode?: string;
        verificationkey?: string;
        xsappname?: string;
    }
}