import { Component } from '@angular/core';
import { MessageService } from 'src/message.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'app';
  messages = [ 'msg1', 'msg2', 'msg3'];
  //messages;

  constructor (private messageService: MessageService) {
    //this.messages = messageService.getMessages().subscribe();
  }
}
