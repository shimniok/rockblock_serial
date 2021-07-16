import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { SocketIoModule, SocketIoConfig } from 'ngx-socket-io';

import { AppComponent } from './app.component';
import { MessageService } from 'src/app/services/message.service';

const config: SocketIoConfig = { url: '/', options: { } };

@NgModule({
  declarations: [AppComponent],
  imports: [BrowserModule, HttpClientModule, SocketIoModule.forRoot(config)],
  providers: [MessageService],
  bootstrap: [AppComponent],
})
export class AppModule {}
