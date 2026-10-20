import { Version } from '@microsoft/sp-core-library';
import { IPropertyPaneConfiguration, PropertyPaneTextField } from '@microsoft/sp-property-pane';
import { BaseClientSideWebPart } from '@microsoft/sp-webpart-base';
import { PORTAL_CSS } from './portal/portalCss';
import { PORTAL_TEMPLATE } from './portal/portalTemplate';
import { PORTAL_ASSETS } from './portal/portalAssets';
import { runPortal } from './portal/runPortal';
import { loadContent } from './portal/ContentLoader';
import { DEFAULT_LISTS } from './portal/defaultLists';

export interface ICorbitXJourneyWebPartProps {
  voiceBaseUrl: string;
}

const STYLE_ID = 'cxj-style';
const FONT_ID = 'cxj-fonts';

export default class CorbitXJourneyWebPart extends BaseClientSideWebPart<ICorbitXJourneyWebPartProps> {
  private renderToken = 0;

  protected onInit(): Promise<void> {
    if (!document.getElementById(STYLE_ID)) {
      const st = document.createElement('style');
      st.id = STYLE_ID; st.textContent = PORTAL_CSS;
      document.head.appendChild(st);
    }
    if (!document.getElementById(FONT_ID)) {
      const l = document.createElement('link');
      l.id = FONT_ID; l.rel = 'stylesheet';
      l.href = 'https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Barlow:ital,wght@0,400;0,500;0,600;0,700;1,500&display=swap';
      document.head.appendChild(l);
    }
    return super.onInit();
  }

  public render(): void {
    const token = ++this.renderToken;
    const webUrl = this.context.pageContext.web.absoluteUrl;
    this.domElement.innerHTML = '<div class="cxj" style="padding:48px 24px;text-align:center;font:600 16px Segoe UI,sans-serif;color:#545557">Kukua is getting ready…</div>';

    loadContent(this.context.spHttpClient, webUrl).catch(() => undefined).then(loaded => {
      if (token !== this.renderToken) return; // a newer render superseded this one
      this.domElement.innerHTML = '<div class="cxj">' + PORTAL_TEMPLATE.replace(/\{\{A(\d+)\}\}/g, (_m, n) => PORTAL_ASSETS[Number(n)]) + '</div>';
      const base = (this.properties.voiceBaseUrl || `${webUrl}/SiteAssets/CorbitX/voice/emily/`).replace(/\/?$/, '/');
      runPortal(loaded ? loaded.lists : DEFAULT_LISTS, loaded ? loaded.posters : {}, PORTAL_ASSETS, { voiceBase: base });
    });
  }

  protected onDispose(): void { this.renderToken++; this.domElement.innerHTML = ''; }

  protected get dataVersion(): Version { return Version.parse('1.0'); }

  protected getPropertyPaneConfiguration(): IPropertyPaneConfiguration {
    return {
      pages: [{
        header: { description: 'All text, tips, FAQs, posters and links are edited in the Corbit X SharePoint lists, not here.' },
        groups: [{ groupName: 'Kukua voice (Emily)', groupFields: [
          PropertyPaneTextField('voiceBaseUrl', { label: 'Voice files folder URL', description: 'Folder holding welcome.mp3, closing.mp3, stage1.mp3 ... Default: SiteAssets/CorbitX/voice/emily/' })
        ] }]
      }]
    };
  }
}
